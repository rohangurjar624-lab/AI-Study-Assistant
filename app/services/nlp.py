import re
import random
from collections import Counter
from typing import Optional

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more",
    "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves", "also", "using", "used", "make",
    "made", "first", "many", "well", "even", "like", "just", "into", "will"
}

GENERIC_FALLBACK_DISTRACTORS = [
    "Mechanism", "Synthesis", "Function", "Component", "Structure",
    "Process", "Molecule", "Regulation", "Pathway", "System",
    "Network", "Hypothesis", "Analysis", "Equation", "Principle"
]


def split_sentences(text: str) -> list[str]:
    """Splits text into meaningful sentences."""
    if not text:
        return []
    # Pattern to match sentence boundaries without splitting abbreviations too aggressively
    raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 15]
    return sentences if sentences else [text.strip()]


def tokenize_words(text: str) -> list[str]:
    """Extracts alphanumeric word tokens."""
    return re.findall(r"\b[A-Za-z0-9_-]{3,}\b", text)


def extract_keywords(text: str, n: int = 10) -> list[str]:
    """
    Extracts the top n keywords from the text based on term frequency
    excluding standard stop words.
    """
    if not text:
        return []

    tokens = tokenize_words(text)
    meaningful = [
        t for t in tokens
        if t.lower() not in STOP_WORDS and not t.isdigit() and len(t) >= 4
    ]

    if not meaningful:
        # Fallback to any words len >= 3
        meaningful = [t for t in tokens if len(t) >= 3]

    counter = Counter()
    case_map = {}
    for t in meaningful:
        lower = t.lower()
        counter[lower] += 1
        if lower not in case_map:
            case_map[lower] = t
        elif t[0].isupper() and not case_map[lower][0].isupper():
            case_map[lower] = t

    most_common = counter.most_common(n)
    return [case_map.get(word, word) for word, _ in most_common]


def summarize(text: str, max_sentences: int = 5) -> str:
    """
    Extractive summarization: scores sentences based on term frequencies
    of key terms and returns the top 3-5 sentences in their original order.
    """
    sentences = split_sentences(text)
    if len(sentences) <= 3:
        return " ".join(sentences)

    target_count = min(max_sentences, max(3, len(sentences) // 2))

    keywords = set(k.lower() for k in extract_keywords(text, n=20))
    if not keywords:
        return " ".join(sentences[:target_count])

    scored = []
    for idx, sentence in enumerate(sentences):
        words = [w.lower() for w in tokenize_words(sentence)]
        if not words:
            continue
        # Frequency of keywords in sentence normalized by length
        score = sum(1 for w in words if w in keywords) / (len(words) ** 0.5)
        # Slight position bias for introductory sentences
        if idx == 0:
            score *= 1.2
        scored.append((score, idx, sentence))

    # Sort by score descending and take top target_count
    top_scored = sorted(scored, key=lambda x: x[0], reverse=True)[:target_count]
    # Re-sort by original index
    top_in_order = sorted(top_scored, key=lambda x: x[1])
    return " ".join(item[2] for item in top_in_order)


def generate_quiz(text: str, n: int = 5) -> list[dict]:
    """
    Generates n MCQ quiz questions from the text.
    Each item:
    {
        "text": "Fill-in-the-blank question...",
        "options": [str, str, str, str],
        "correct_index": int (0..3),
        "explanation": "Context sentence explaining the answer.",
        "topic": "Keyword/Topic name"
    }
    """
    sentences = split_sentences(text)
    keywords = extract_keywords(text, n=25)

    if not keywords:
        keywords = ["Concept", "System", "Function", "Process"]

    questions = []
    used_pairs = set()

    # Search for candidate sentences containing keywords
    for kw in keywords:
        if len(questions) >= n:
            break

        pattern = re.compile(rf"\b({re.escape(kw)})\b", re.IGNORECASE)
        for s in sentences:
            if (s, kw.lower()) in used_pairs or len(s) < 25:
                continue

            match = pattern.search(s)
            if match:
                matched_text = match.group(1)
                # Create fill in the blank question
                q_text = pattern.sub("_____", s, count=1)
                if "_____" not in q_text:
                    continue

                used_pairs.add((s, kw.lower()))

                # Distractors: pick 3 distinct keywords not equal to the answer
                distractors = [
                    k for k in keywords
                    if k.lower() != matched_text.lower()
                ]
                # If we don't have enough distractors, supplement with generic fallbacks
                if len(distractors) < 3:
                    for fb in GENERIC_FALLBACK_DISTRACTORS:
                        if fb.lower() != matched_text.lower() and fb not in distractors:
                            distractors.append(fb)
                        if len(distractors) >= 3:
                            break

                chosen_distractors = distractors[:3]
                options = chosen_distractors + [matched_text]
                rnd = random.Random(hash(s) + len(questions) + hash(kw))
                rnd.shuffle(options)
                correct_idx = options.index(matched_text)

                explanation = (
                    f"'{matched_text}' is the correct answer. Context: \"{s}\""
                )
                topic = matched_text.capitalize()

                questions.append({
                    "text": f"Complete the statement: {q_text}",
                    "options": options,
                    "correct_index": correct_idx,
                    "explanation": explanation,
                    "topic": topic
                })
                break

    # If we still need questions, generate conceptual recognition questions from remaining keywords
    if len(questions) < n:
        for kw in keywords:
            if len(questions) >= n:
                break
            if any(q.get("topic", "").lower() == kw.lower() for q in questions):
                continue
            distractors = [k for k in keywords if k.lower() != kw.lower()][:3]
            while len(distractors) < 3:
                distractors.append(GENERIC_FALLBACK_DISTRACTORS[len(distractors) % len(GENERIC_FALLBACK_DISTRACTORS)])
            options = distractors[:3] + [kw]
            rnd = random.Random(hash(kw) + len(questions))
            rnd.shuffle(options)
            correct_idx = options.index(kw)

            questions.append({
                "text": f"Which of the following key concepts is discussed in the context of this study topic?",
                "options": options,
                "correct_index": correct_idx,
                "explanation": f"'{kw}' is a primary subject concept identified in the notes.",
                "topic": kw.capitalize()
            })

    return questions[:n]


def generate_flashcards(text: str, n: int = 10) -> list[dict]:
    """
    Generates n flashcard dictionaries with 'front' (term/keyword)
    and 'back' (definition or informative sentence).
    """
    sentences = split_sentences(text)
    keywords = extract_keywords(text, n=n * 2)

    cards = []
    used_terms = set()

    for kw in keywords:
        if len(cards) >= n:
            break
        if kw.lower() in used_terms:
            continue

        pattern = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
        best_sentence = None
        best_score = -1

        for s in sentences:
            if pattern.search(s):
                score = 0
                lower_s = s.lower()
                # Prioritize definitional sentences
                if any(ind in lower_s for ind in [" is ", " are ", " defined as ", " refers to ", " means "]):
                    score += 5
                if len(s) < 180:
                    score += 2
                if score > best_score:
                    best_score = score
                    best_sentence = s

        if best_sentence:
            used_terms.add(kw.lower())
            cards.append({
                "front": kw.capitalize(),
                "back": best_sentence
            })

    # If still fewer than n cards, fill with sentences
    if len(cards) < n:
        for idx, s in enumerate(sentences):
            if len(cards) >= n:
                break
            if len(s) >= 30 and not any(c["back"] == s for c in cards):
                cards.append({
                    "front": f"Key Concept #{len(cards) + 1}",
                    "back": s
                })

    return cards[:n]
