import io
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from app.services import extract, nlp, srs, llm
from app.services.extract import ValidationError, ScannedPDFError, ExtractError
from werkzeug.datastructures import FileStorage


SAMPLE_TEXT = (
    "Photosynthesis is a chemical process that occurs in plants, algae, and some types of bacteria. "
    "It uses sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar. "
    "Inside plant cells, small structures called chloroplasts house the green pigment chlorophyll. "
    "The process occurs in two main phases: light-dependent reactions and light-independent reactions. "
    "In the light-dependent reactions, solar energy is converted into chemical bonds of ATP and NADPH. "
    "The Calvin cycle then utilizes ATP and NADPH to assemble carbohydrates from atmospheric carbon dioxide. "
    "RuBisCO is the essential enzyme responsible for carbon fixation in the stroma of chloroplasts."
)


# ==========================================
# 1. EXTRACT SERVICE TESTS
# ==========================================

def test_allowed_file():
    assert extract.allowed_file("notes.txt") is True
    assert extract.allowed_file("lecture.pdf") is True
    assert extract.allowed_file("script.py") is False
    assert extract.allowed_file("image.png") is False
    assert extract.allowed_file("") is False
    assert extract.allowed_file("no_extension") is False


def test_validate_text_length():
    short_text = "Too short."
    with pytest.raises(ValidationError) as exc:
        extract.validate_text_length(short_text)
    assert "too short" in str(exc.value)

    long_text = "word " * 11000  # > 50,000 characters
    with pytest.raises(ValidationError) as exc:
        extract.validate_text_length(long_text)
    assert "too long" in str(exc.value)

    valid = extract.validate_text_length(SAMPLE_TEXT)
    assert len(valid) >= 200


def test_extract_txt_file_utf8():
    content_bytes = SAMPLE_TEXT.encode("utf-8")
    file_storage = FileStorage(
        stream=io.BytesIO(content_bytes),
        filename="notes.txt",
        content_type="text/plain",
    )
    text, filename, source_type = extract.extract_from_file(file_storage)
    assert filename == "notes.txt"
    assert source_type == "txt"
    assert "Photosynthesis" in text


def test_extract_txt_file_latin1_fallback():
    latin_bytes = (SAMPLE_TEXT + " Café résumé").encode("latin-1")
    file_storage = FileStorage(
        stream=io.BytesIO(latin_bytes),
        filename="lecture_latin.txt",
        content_type="text/plain",
    )
    text, filename, source_type = extract.extract_from_file(file_storage)
    assert source_type == "txt"
    assert "Caf" in text


def test_extract_empty_file():
    file_storage = FileStorage(
        stream=io.BytesIO(b""),
        filename="empty.txt",
        content_type="text/plain",
    )
    with pytest.raises(ValidationError) as exc:
        extract.extract_from_file(file_storage)
    assert "empty" in str(exc.value).lower()


def test_extract_invalid_extension():
    file_storage = FileStorage(
        stream=io.BytesIO(b"some content here"),
        filename="malicious.exe",
        content_type="application/octet-stream",
    )
    with pytest.raises(ValidationError) as exc:
        extract.extract_from_file(file_storage)
    assert "Only .txt and .pdf" in str(exc.value)


@patch("pypdf.PdfReader")
def test_extract_pdf_valid(mock_reader_cls):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = SAMPLE_TEXT
    mock_instance = MagicMock()
    mock_instance.pages = [mock_page]
    mock_reader_cls.return_value = mock_instance

    file_storage = FileStorage(
        stream=io.BytesIO(b"%PDF-1.4 mock pdf bytes"),
        filename="biology.pdf",
        content_type="application/pdf",
    )
    text, filename, source_type = extract.extract_from_file(file_storage)
    assert filename == "biology.pdf"
    assert source_type == "pdf"
    assert "Photosynthesis" in text


@patch("pypdf.PdfReader")
def test_extract_scanned_pdf_error(mock_reader_cls):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""  # No text (scanned image)
    mock_instance = MagicMock()
    mock_instance.pages = [mock_page]
    mock_reader_cls.return_value = mock_instance

    file_storage = FileStorage(
        stream=io.BytesIO(b"%PDF-1.4 scanned image"),
        filename="scanned_handout.pdf",
        content_type="application/pdf",
    )
    with pytest.raises(ScannedPDFError) as exc:
        extract.extract_from_file(file_storage)
    assert "PDF looks scanned" in str(exc.value)


# ==========================================
# 2. SRS SERVICE TESTS (SM-2 ALGORITHM)
# ==========================================

def test_srs_invalid_grade():
    with pytest.raises(ValueError):
        srs.calculate_sm2(grade=6, repetitions=0, interval_days=0, ease_factor=2.5)
    with pytest.raises(ValueError):
        srs.calculate_sm2(grade=-1, repetitions=0, interval_days=0, ease_factor=2.5)


def test_srs_initial_successful_reps():
    base_date = date(2026, 10, 22)
    reps, interval, ef, due = srs.calculate_sm2(5, 0, 0, 2.5, today=base_date)
    assert reps == 1
    assert interval == 1
    assert ef == 2.6
    assert due == base_date + timedelta(days=1)

    reps, interval, ef, due = srs.calculate_sm2(4, reps, interval, ef, today=due)
    assert reps == 2
    assert interval == 6
    assert ef == 2.6
    assert due == base_date + timedelta(days=1 + 6)

    reps, interval, ef, due = srs.calculate_sm2(5, reps, interval, ef, today=due)
    assert reps == 3
    assert interval == 16
    assert ef == 2.7


def test_srs_failed_recall_resets_repetitions():
    base_date = date(2026, 10, 22)
    reps, interval, ef, due = srs.calculate_sm2(grade=2, repetitions=4, interval_days=30, ease_factor=2.5, today=base_date)
    assert reps == 0
    assert interval == 1
    assert ef < 2.5
    assert due == base_date + timedelta(days=1)


def test_srs_ease_factor_floor():
    reps, interval, ef, due = srs.calculate_sm2(grade=0, repetitions=0, interval_days=1, ease_factor=1.35)
    assert ef == 1.3
    reps, interval, ef, due = srs.calculate_sm2(grade=0, repetitions=0, interval_days=1, ease_factor=1.3)
    assert ef == 1.3


# ==========================================
# 3. NLP OFFLINE ENGINE TESTS
# ==========================================

def test_nlp_extract_keywords():
    keywords = nlp.extract_keywords(SAMPLE_TEXT, n=5)
    assert isinstance(keywords, list)
    assert len(keywords) == 5
    for kw in keywords:
        assert kw.lower() not in nlp.STOP_WORDS
        assert len(kw) >= 3


def test_nlp_summarize_shape():
    summary = nlp.summarize(SAMPLE_TEXT, max_sentences=4)
    assert isinstance(summary, str)
    assert len(summary) > 80
    assert "Photosynthesis" in summary

    # Short text
    short = "Sentence one. Sentence two."
    assert nlp.summarize(short) == short


def test_nlp_generate_quiz_shape():
    questions = nlp.generate_quiz(SAMPLE_TEXT, n=5)
    assert len(questions) == 5

    for q in questions:
        assert "text" in q
        assert "options" in q
        assert len(q["options"]) == 4
        assert "correct_index" in q
        assert 0 <= q["correct_index"] <= 3
        assert "explanation" in q
        assert len(q["explanation"]) > 5
        assert "topic" in q


def test_nlp_generate_flashcards_shape():
    cards = nlp.generate_flashcards(SAMPLE_TEXT, n=4)
    assert len(cards) == 4
    for c in cards:
        assert "front" in c
        assert "back" in c
        assert len(c["front"]) > 0
        assert len(c["back"]) > 10


# ==========================================
# 4. LLM ENGINE & FALLBACK TESTS
# ==========================================

def test_llm_fallback_when_no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    summary = llm.summarize(SAMPLE_TEXT)
    assert isinstance(summary, str)
    assert len(summary) > 50

    keywords = llm.extract_keywords(SAMPLE_TEXT, n=4)
    assert len(keywords) == 4

    quiz, engine = llm.generate_quiz_with_engine(SAMPLE_TEXT, n=3)
    assert engine == "offline"
    assert len(quiz) == 3

    # convenience wrapper
    quiz_wrap = llm.generate_quiz(SAMPLE_TEXT, n=3)
    assert len(quiz_wrap) == 3

    cards = llm.generate_flashcards(SAMPLE_TEXT, n=3)
    assert len(cards) == 3


@patch("app.services.llm.get_anthropic_client")
def test_llm_summarize_mocked(mock_client_factory):
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text="This is an AI generated summary of photosynthesis in three sentences.")]
    mock_client.messages.create.return_value = mock_msg
    mock_client_factory.return_value = mock_client

    result = llm.summarize(SAMPLE_TEXT)
    assert "AI generated summary" in result


@patch("app.services.llm.get_anthropic_client")
def test_llm_extract_keywords_mocked(mock_client_factory):
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='```json\n["Chloroplast", "Calvin Cycle", "RuBisCO"]\n```')]
    mock_client.messages.create.return_value = mock_msg
    mock_client_factory.return_value = mock_client

    keywords = llm.extract_keywords(SAMPLE_TEXT, n=3)
    assert keywords == ["Chloroplast", "Calvin Cycle", "RuBisCO"]


@patch("app.services.llm.get_anthropic_client")
def test_llm_quiz_valid_response(mock_client_factory):
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [
        MagicMock(
            text='''[
                {
                    "text": "What is the primary site of photosynthesis?",
                    "options": ["Mitochondria", "Chloroplasts", "Nucleus", "Ribosome"],
                    "correct_index": 1,
                    "explanation": "Photosynthesis occurs in chloroplasts.",
                    "topic": "Cell Biology"
                }
            ]'''
        )
    ]
    mock_client.messages.create.return_value = mock_msg
    mock_client_factory.return_value = mock_client

    quiz, engine = llm.generate_quiz_with_engine(SAMPLE_TEXT, n=1)
    assert engine == "llm"
    assert len(quiz) == 1
    assert quiz[0]["text"] == "What is the primary site of photosynthesis?"
    assert quiz[0]["correct_index"] == 1
    assert len(quiz[0]["options"]) == 4


@patch("app.services.llm.get_anthropic_client")
def test_llm_flashcards_mocked(mock_client_factory):
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [
        MagicMock(
            text='''[
                {"front": "RuBisCO", "back": "Carbon fixation enzyme."},
                {"front": "Thylakoid", "back": "Membrane sac where light reactions occur."}
            ]'''
        )
    ]
    mock_client.messages.create.return_value = mock_msg
    mock_client_factory.return_value = mock_client

    cards = llm.generate_flashcards(SAMPLE_TEXT, n=2)
    assert len(cards) == 2
    assert cards[0]["front"] == "RuBisCO"


@patch("app.services.llm.get_anthropic_client")
def test_llm_invalid_json_falls_back_to_offline(mock_client_factory):
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text="Sorry, I am not able to output valid JSON right now.")]
    mock_client.messages.create.return_value = mock_msg
    mock_client_factory.return_value = mock_client

    quiz, engine = llm.generate_quiz_with_engine(SAMPLE_TEXT, n=2)
    assert engine == "offline"
    assert len(quiz) == 2


@patch("app.services.llm.get_anthropic_client")
def test_llm_timeout_falls_back_to_offline(mock_client_factory):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = TimeoutError("Connection timed out after 20s")
    mock_client_factory.return_value = mock_client

    quiz, engine = llm.generate_quiz_with_engine(SAMPLE_TEXT, n=2)
    assert engine == "offline"
    assert len(quiz) == 2


def test_prepare_text_truncation():
    long_str = "A" * 15000
    truncated, was_trunc = llm.prepare_text(long_str)
    assert was_trunc is True
    assert len(truncated) < 15000
    assert "truncated" in truncated


def test_nlp_edge_cases():
    # Empty inputs
    assert nlp.split_sentences("") == []
    assert nlp.split_sentences("Short.") == ["Short."]
    assert nlp.tokenize_words("") == []
    assert nlp.extract_keywords("") == []

    # Text with only stopwords and short tokens
    assert len(nlp.extract_keywords("the is at on if and or but so to do", n=3)) > 0

    # Text with capital letter variance
    cap_text = "Photosynthesis creates energy. PHOTOSYNTHESIS occurs in plants."
    kws = nlp.extract_keywords(cap_text, n=2)
    assert any("Photosynthesis" in k for k in kws)

    # Summarize with no keywords
    simple_sentences = "This is a test. That is another sentence. Here is a third line."
    s_res = nlp.summarize(simple_sentences)
    assert len(s_res) > 0

    # generate_quiz with conceptual fallback and generic distractors padding
    short_notes = "Alpha beta gamma delta. Epsilon zeta eta theta."
    quiz = nlp.generate_quiz(short_notes, n=6)
    assert len(quiz) == 6

    # generate_flashcards filler when cards < n
    fill_text = (
        "Cell biology investigates the molecular components of living organisms. "
        "Mitochondria produce cellular adenosine triphosphate through respiration. "
        "The nucleus stores genomic DNA in chromosomes. "
        "Ribosomes synthesize polypeptides from messenger RNA templates."
    )
    cards = nlp.generate_flashcards(fill_text, n=8)
    assert len(cards) == 8


@patch("app.services.llm.get_anthropic_client")
def test_llm_markdown_fence_and_validation(mock_client_factory):
    mock_client = MagicMock()
    # Quiz with ```json fence
    mock_msg_quiz = MagicMock()
    mock_msg_quiz.content = [MagicMock(text='''```json
    [
        {
            "text": "What is ATP?",
            "options": ["Energy carrier", "Lipid", "Vitamin", "Mineral"],
            "correct_index": 0,
            "explanation": "ATP carries chemical energy.",
            "topic": "Bioenergetics"
        }
    ]
    ```''')]
    mock_client.messages.create.return_value = mock_msg_quiz
    mock_client_factory.return_value = mock_client

    quiz, engine = llm.generate_quiz_with_engine(SAMPLE_TEXT, n=1)
    assert engine == "llm"
    assert quiz[0]["topic"] == "Bioenergetics"

    # Flashcard with ```json fence
    mock_msg_fc = MagicMock()
    mock_msg_fc.content = [MagicMock(text='''```json
    [
        {"front": "ATP", "back": "Adenosine Triphosphate"}
    ]
    ```''')]
    mock_client.messages.create.return_value = mock_msg_fc
    fc = llm.generate_flashcards(SAMPLE_TEXT, n=1)
    assert fc[0]["front"] == "ATP"


@patch("anthropic.Anthropic")
def test_get_anthropic_client_handles_init_error(mock_anthropic):
    mock_anthropic.side_effect = Exception("SDK Error")
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "dummy-key"}):
        client = llm.get_anthropic_client()
        assert client is None

