from datetime import datetime, timezone, date, timedelta
from app import create_app
from app.extensions import db
from app.models import User, Note, Quiz, Question, Attempt, AttemptAnswer, Flashcard
from app.services import nlp

app = create_app()


def seed_database():
    with app.app_context():
        # Check if demo user already exists
        demo = User.query.filter_by(email="demo@example.com").first()
        if demo:
            print("Cleaning up old demo user data...")
            db.session.delete(demo)
            db.session.commit()

        print("Creating demo account (demo@example.com / DemoPass123!)...")
        demo = User(
            username="demo_student",
            email="demo@example.com",
            streak_count=4,
            last_study_date=date.today(),
            last_login_at=datetime.now(timezone.utc)
        )
        demo.set_password("DemoPass123!")
        db.session.add(demo)
        db.session.commit()

        # Sample Note 1: Biology
        bio_text = (
            "Photosynthesis is the fundamental biological process by which green plants, algae, and cyanobacteria "
            "convert light energy into chemical energy stored in glucose molecules. In plant cells, this intricate "
            "reaction takes place within specialized organelles known as chloroplasts, specifically within the thylakoid "
            "membranes and the surrounding fluid called the stroma. The process is divided into two interdependent phases: "
            "the light-dependent reactions and the light-independent reactions, commonly known as the Calvin cycle.\n\n"
            "During the light-dependent reactions, chlorophyll pigments absorb photons of light, exciting electrons that "
            "travel along an electron transport chain. This movement pumps protons into the thylakoid lumen, establishing "
            "an electrochemical gradient that powers ATP synthase to generate ATP. Concurrently, photolysis splits water "
            "molecules into oxygen gas, protons, and electrons. The energetic electrons reduce NADP+ into NADPH.\n\n"
            "In the second stage, the Calvin cycle utilizes the ATP and NADPH produced during the light reactions to fix "
            "atmospheric carbon dioxide into high-energy sugars like glyceraldehyde 3-phosphate. The key enzyme responsible "
            "for carbon fixation is RuBisCO, one of the most abundant enzymes on Earth. Through cyclic regeneration of "
            "ribulose 1,5-bisphosphate, glucose is synthesized, which serves as cellular fuel and structural cellulose for the organism."
        )

        note1 = Note(
            title="Biology: Photosynthesis and the Calvin Cycle",
            content=bio_text,
            source_type="paste",
            original_filename=None,
            summary=nlp.summarize(bio_text),
            keywords=nlp.extract_keywords(bio_text, n=10),
            user_id=demo.id
        )
        db.session.add(note1)
        db.session.flush()

        # Sample Note 2: Computer Science
        cs_text = (
            "Operating systems manage computer hardware resources and provide a stable execution environment for software applications. "
            "A core responsibility of the kernel is process scheduling, which dictates how the Central Processing Unit (CPU) allocates "
            "execution time among concurrent processes. Common scheduling algorithms include First-Come First-Served, Shortest Job Next, "
            "Priority Scheduling, and Round Robin. In Round Robin scheduling, each process is granted a fixed quantum of CPU time before "
            "being preempted, ensuring fairness and responsiveness in interactive desktop environments.\n\n"
            "Another critical challenge in operating systems design is concurrency management and the avoidance of deadlocks. A deadlock "
            "occurs when a set of processes are permanently blocked because each process holds a resource while awaiting another resource "
            "held by another process. The four necessary Coffman conditions for deadlocks are mutual exclusion, hold and wait, no preemption, "
            "and circular wait. Modern kernels use algorithms like Dijkstra's Banker's algorithm for deadlock avoidance.\n\n"
            "Memory management is maintained via virtual memory, which separates logical user addresses from physical RAM. Using paging, "
            "the operating system divides virtual memory into fixed-sized blocks called pages, mapped to physical frames via page tables. "
            "When a requested page is not resident in physical RAM, a page fault exception triggers the operating system to retrieve "
            "the missing page from secondary storage."
        )

        note2 = Note(
            title="Computer Science: OS Process Scheduling & Memory Management",
            content=cs_text,
            source_type="paste",
            original_filename=None,
            summary=nlp.summarize(cs_text),
            keywords=nlp.extract_keywords(cs_text, n=10),
            user_id=demo.id
        )
        db.session.add(note2)
        db.session.flush()

        # Generate Quiz for Note 1
        quiz1 = Quiz(
            user_id=demo.id,
            note_id=note1.id,
            title="Quiz: Photosynthesis Fundamentals",
            engine_used="offline"
        )
        db.session.add(quiz1)
        db.session.flush()

        q1_data = [
            {
                "text": "Where do the light-dependent reactions take place inside plant cells?",
                "options": ["Thylakoid membranes", "Stroma", "Cell wall", "Mitochondria"],
                "correct_index": 0,
                "explanation": "Light-dependent reactions occur within the thylakoid membranes containing chlorophyll.",
                "topic": "Chloroplasts"
            },
            {
                "text": "What is the primary enzyme responsible for carbon fixation in the Calvin cycle?",
                "options": ["ATP Synthase", "RuBisCO", "DNA Polymerase", "Amylase"],
                "correct_index": 1,
                "explanation": "RuBisCO catalyzes the fixation of CO2 into organic molecules.",
                "topic": "Calvin Cycle"
            },
            {
                "text": "What molecules produced in the light reactions provide energy for the Calvin cycle?",
                "options": ["Oxygen and Glucose", "ATP and NADPH", "Water and Carbon Dioxide", "ADP and NADP+"],
                "correct_index": 1,
                "explanation": "ATP and NADPH power the sugar-building reactions in the stroma.",
                "topic": "Bioenergetics"
            },
            {
                "text": "What byproduct is released when water molecules undergo photolysis?",
                "options": ["Carbon dioxide", "Methane", "Oxygen", "Nitrogen"],
                "correct_index": 2,
                "explanation": "Water splitting generates oxygen gas released into the atmosphere.",
                "topic": "Photolysis"
            },
            {
                "text": "Which organelle houses the machinery for photosynthetic reactions?",
                "options": ["Vacuole", "Ribosome", "Endoplasmic reticulum", "Chloroplast"],
                "correct_index": 3,
                "explanation": "Photosynthesis takes place within chloroplasts in photosynthetic organisms.",
                "topic": "Chloroplasts"
            }
        ]

        created_questions = []
        for qd in q1_data:
            q = Question(
                quiz_id=quiz1.id,
                text=qd["text"],
                options=qd["options"],
                correct_index=qd["correct_index"],
                explanation=qd["explanation"],
                topic=qd["topic"]
            )
            db.session.add(q)
            created_questions.append(q)
        db.session.flush()

        # Add Attempts for Quiz 1 to seed realistic dashboard charts!
        attempt1 = Attempt(
            user_id=demo.id,
            quiz_id=quiz1.id,
            score=4,
            total=5,
            duration_seconds=95,
            taken_at=datetime.now(timezone.utc) - timedelta(days=2)
        )
        db.session.add(attempt1)
        db.session.flush()

        for idx, q in enumerate(created_questions):
            ans = AttemptAnswer(
                attempt_id=attempt1.id,
                question_id=q.id,
                selected_index=q.correct_index if idx != 1 else 0,  # Missed question 1
                is_correct=(idx != 1)
            )
            db.session.add(ans)

        attempt2 = Attempt(
            user_id=demo.id,
            quiz_id=quiz1.id,
            score=5,
            total=5,
            duration_seconds=78,
            taken_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.session.add(attempt2)
        db.session.flush()

        for q in created_questions:
            ans = AttemptAnswer(
                attempt_id=attempt2.id,
                question_id=q.id,
                selected_index=q.correct_index,
                is_correct=True
            )
            db.session.add(ans)

        # Generate Flashcards
        today = date.today()
        sample_cards = [
            (
                "Chloroplast",
                "Specialized double-membraned organelle in plant cells where photosynthesis occurs.",
                note1.id,
                today  # Due today
            ),
            (
                "RuBisCO",
                "The essential enzyme that fixes atmospheric carbon dioxide in the Calvin cycle.",
                note1.id,
                today  # Due today
            ),
            (
                "Thylakoid",
                "Flattened sac inside the chloroplast, bound by membranes on which the light reactions take place.",
                note1.id,
                today + timedelta(days=2)  # Future
            ),
            (
                "Virtual Memory",
                "Memory management technique separating user logical memory from physical memory using paging.",
                note2.id,
                today  # Due today
            ),
            (
                "Round Robin Scheduling",
                "Preemptive CPU scheduling algorithm assigning each process a fixed time slice (quantum).",
                note2.id,
                today + timedelta(days=5)  # Future
            ),
            (
                "Deadlock",
                "A state where a group of processes are blocked because each is waiting for a resource held by another.",
                note2.id,
                today  # Due today
            )
        ]

        for front, back, nid, due in sample_cards:
            fc = Flashcard(
                user_id=demo.id,
                note_id=nid,
                front=front,
                back=back,
                ease_factor=2.5,
                interval_days=1 if due == today else 3,
                repetitions=1,
                due_date=due
            )
            db.session.add(fc)

        db.session.commit()
        print("Database successfully seeded with demo student, notes, quizzes, attempts, and flashcards!")


if __name__ == "__main__":
    seed_database()
