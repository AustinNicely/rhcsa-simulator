"""
Flashcard Quiz Mode - Quick recall training for RHCSA exam.
Tests knowledge with Q&A flashcards for rapid review.
"""

import random
import logging
from utils import formatters as fmt
from utils.helpers import confirm_action


logger = logging.getLogger(__name__)


class FlashcardContent:
    """
    Flashcard Q&A content organized by topic.
    Each card has: question, answer, hint, and difficulty.
    """

    CARDS = {
        "users_groups": [
            {
                "question": "What file contains encrypted user passwords?",
                "answer": "/etc/shadow",
                "hint": "Not /etc/passwd - that's the user account info",
                "difficulty": "easy"
            },
            {
                "question": "How do you add user 'john' to group 'wheel' WITHOUT removing existing groups?",
                "answer": "usermod -aG wheel john",
                "hint": "The -a flag is critical here (append)",
                "difficulty": "exam"
            },
            {
                "question": "What does 'usermod -G wheel john' do differently than 'usermod -aG wheel john'?",
                "answer": "-G alone REPLACES all supplementary groups with just 'wheel'. -aG APPENDS wheel to existing groups.",
                "hint": "One removes, one adds",
                "difficulty": "exam"
            },
            {
                "question": "How do you force a user to change their password on next login?",
                "answer": "chage -d 0 username",
                "hint": "Think of 'chage' - change age, -d sets last change date",
                "difficulty": "exam"
            },
            {
                "question": "What command shows a user's UID, GID, and group memberships?",
                "answer": "id username",
                "hint": "Simple 2-letter command",
                "difficulty": "easy"
            },
            {
                "question": "How do you create a user that cannot log in interactively?",
                "answer": "useradd -s /sbin/nologin username",
                "hint": "Set the shell to something that denies login",
                "difficulty": "medium"
            },
            {
                "question": "What does UID 0 signify?",
                "answer": "Root user (superuser privileges)",
                "hint": "The most powerful user",
                "difficulty": "easy"
            },
            {
                "question": "Where should you place sudo configuration files for persistence?",
                "answer": "/etc/sudoers.d/",
                "hint": "It's a directory for drop-in files, not the main sudoers file",
                "difficulty": "exam"
            },
            {
                "question": "What command safely edits sudoers with syntax checking?",
                "answer": "visudo",
                "hint": "It has 'sudo' in the name",
                "difficulty": "easy"
            },
            {
                "question": "How do you lock a user account?",
                "answer": "usermod -L username (or passwd -l username)",
                "hint": "L for Lock",
                "difficulty": "medium"
            },
            {
                "question": "What's the difference between account expiration and password expiration?",
                "answer": "Account expiration (chage -E) disables the entire account. Password expiration (chage -M) just requires a new password.",
                "hint": "One locks you out completely, the other just requires a password change",
                "difficulty": "exam"
            },
            {
                "question": "What command shows password aging information for a user?",
                "answer": "chage -l username",
                "hint": "chage with list flag",
                "difficulty": "medium"
            },
        ],

        "permissions": [
            {
                "question": "What is the numeric value of rwxr-xr-- ?",
                "answer": "754",
                "hint": "rwx=7, r-x=5, r--=4",
                "difficulty": "easy"
            },
            {
                "question": "What does the SGID bit do on a DIRECTORY?",
                "answer": "New files/directories inherit the group ownership of the parent directory",
                "hint": "Think 'group inheritance'",
                "difficulty": "exam"
            },
            {
                "question": "What does the sticky bit do on a directory?",
                "answer": "Only the owner of a file (or root) can delete it, even if others have write permission",
                "hint": "Think /tmp - everyone can write, but can't delete others' files",
                "difficulty": "exam"
            },
            {
                "question": "How do you set SUID, SGID, and sticky bit together numerically?",
                "answer": "chmod 7xxx file (e.g., 7755) - SUID=4, SGID=2, Sticky=1",
                "hint": "4+2+1=7 as the first digit",
                "difficulty": "hard"
            },
            {
                "question": "What does a capital S or T mean in permission output (ls -l)?",
                "answer": "Special permission is set but execute permission is NOT set (broken/unusual)",
                "hint": "Lowercase s/t means execute IS set",
                "difficulty": "exam"
            },
            {
                "question": "How do you set SGID on a directory?",
                "answer": "chmod g+s directory OR chmod 2xxx directory",
                "hint": "g+s = group + special",
                "difficulty": "exam"
            },
            {
                "question": "How do you view ACLs on a file?",
                "answer": "getfacl filename",
                "hint": "get file ACL",
                "difficulty": "easy"
            },
            {
                "question": "How do you set a DEFAULT ACL on a directory for inheritance?",
                "answer": "setfacl -d -m u:username:rwx directory",
                "hint": "-d for default, -m for modify",
                "difficulty": "exam"
            },
            {
                "question": "How do you remove ALL ACLs from a file?",
                "answer": "setfacl -b filename",
                "hint": "-b for 'blank' or remove all",
                "difficulty": "medium"
            },
            {
                "question": "What indicates a file has an ACL in ls -l output?",
                "answer": "A + sign at the end of permissions: -rw-r--r--+",
                "hint": "Look at the end of the permission string",
                "difficulty": "easy"
            },
            {
                "question": "What command changes ownership recursively?",
                "answer": "chown -R user:group directory",
                "hint": "-R for recursive",
                "difficulty": "easy"
            },
            {
                "question": "What's the difference between -perm 755 and -perm -755 in find?",
                "answer": "-perm 755 = exactly these permissions. -perm -755 = at least these permissions (may have more)",
                "hint": "The dash means 'at least'",
                "difficulty": "exam"
            },
        ],

        "essential_tools": [
            {
                "question": "What tar option compresses with gzip?",
                "answer": "-z (lowercase z)",
                "hint": "z is for gzip, like the 'z' in gzip",
                "difficulty": "easy"
            },
            {
                "question": "What tar option compresses with bzip2?",
                "answer": "-j (lowercase j)",
                "hint": "j comes after i in alphabet, bzip2 is 'better' compression",
                "difficulty": "easy"
            },
            {
                "question": "What tar option compresses with xz?",
                "answer": "-J (CAPITAL J)",
                "hint": "Capital J for xz (the 'extra' compression)",
                "difficulty": "medium"
            },
            {
                "question": "How do you extract a tar archive to a specific directory?",
                "answer": "tar -xvf archive.tar -C /path/to/directory",
                "hint": "-C for 'change directory'",
                "difficulty": "exam"
            },
            {
                "question": "What's the difference between a hard link and symbolic link?",
                "answer": "Hard link = same inode (data), can't cross filesystems, survives original deletion. Symlink = points to path, can cross filesystems, breaks if original deleted.",
                "hint": "Hard links are 'harder' to break",
                "difficulty": "exam"
            },
            {
                "question": "How do you create a symbolic link?",
                "answer": "ln -s target linkname",
                "hint": "-s for symbolic/soft",
                "difficulty": "easy"
            },
            {
                "question": "How do you verify two files are hard links (same inode)?",
                "answer": "ls -i (shows inode numbers)",
                "hint": "-i for inode",
                "difficulty": "medium"
            },
            {
                "question": "How do you find all SUID files on the system?",
                "answer": "find / -perm -4000 2>/dev/null",
                "hint": "4 for SUID, - for 'at least'",
                "difficulty": "exam"
            },
            {
                "question": "How do you find all SGID files on the system?",
                "answer": "find / -perm -2000 2>/dev/null",
                "hint": "2 for SGID",
                "difficulty": "exam"
            },
            {
                "question": "What does 2>/dev/null do?",
                "answer": "Redirects stderr (error messages) to nowhere, suppressing them",
                "hint": "2 = stderr, /dev/null = black hole",
                "difficulty": "medium"
            },
            {
                "question": "How do you copy a directory preserving all attributes (permissions, ownership, timestamps)?",
                "answer": "cp -a source destination (archive mode)",
                "hint": "-a for archive = preserve everything",
                "difficulty": "exam"
            },
            {
                "question": "What find option executes a command for each found file?",
                "answer": "-exec command {} \\;",
                "hint": "{} is placeholder, \\; ends the command",
                "difficulty": "exam"
            },
            {
                "question": "How do you find files modified in the last 7 days?",
                "answer": "find /path -mtime -7",
                "hint": "-mtime for modification time, - means 'less than'",
                "difficulty": "medium"
            },
            {
                "question": "How do you find files larger than 100MB?",
                "answer": "find /path -size +100M",
                "hint": "+ means 'greater than', M for megabytes",
                "difficulty": "medium"
            },
            {
                "question": "What's the difference between find -exec {} \\; and -exec {} +?",
                "answer": "\\; runs command once per file. + runs command once with all files as arguments (faster).",
                "hint": "; = one at a time, + = all at once",
                "difficulty": "hard"
            },
        ],
    }

    @classmethod
    def get_cards_for_topic(cls, topic):
        """Get all flashcards for a topic."""
        return cls.CARDS.get(topic, [])

    @classmethod
    def get_all_topics(cls):
        """Get list of all topics with flashcards."""
        return list(cls.CARDS.keys())

    @classmethod
    def get_random_cards(cls, count=10, topic=None, difficulty=None):
        """Get random selection of flashcards."""
        if topic:
            cards = cls.CARDS.get(topic, [])
        else:
            cards = []
            for topic_cards in cls.CARDS.values():
                cards.extend(topic_cards)

        if difficulty:
            cards = [c for c in cards if c['difficulty'] == difficulty]

        if len(cards) <= count:
            random.shuffle(cards)
            return cards

        return random.sample(cards, count)


class FlashcardMode:
    """
    Flashcard quiz mode interface.
    """

    def __init__(self):
        """Initialize flashcard mode."""
        self.logger = logging.getLogger(__name__)
        self.correct = 0
        self.incorrect = 0
        self.skipped = 0

    def start(self):
        """Start flashcard quiz mode."""
        while True:
            fmt.clear_screen()
            fmt.print_header("FLASHCARD QUIZ MODE")

            print("Test your RHCSA knowledge with quick Q&A flashcards!")
            print()
            print(fmt.bold("Select Quiz Type:"))
            print()

            topics = FlashcardContent.get_all_topics()

            # Show topic options
            print(fmt.dim("=== By Topic ==="))
            for i, topic in enumerate(topics, 1):
                topic_name = topic.replace('_', ' ').title()
                card_count = len(FlashcardContent.get_cards_for_topic(topic))
                fmt.print_menu_option(i, f"{topic_name}", f"({card_count} cards)")

            print()
            print(fmt.dim("=== Mixed Quiz ==="))
            fmt.print_menu_option(len(topics) + 1, "Quick Quiz (10 random)", "All topics mixed")
            fmt.print_menu_option(len(topics) + 2, "Full Quiz (all cards)", "Complete review")
            print()
            fmt.print_menu_option('Q', "Back to Main Menu")

            choice = input("\nSelect option: ").strip()

            if choice.lower() == 'q':
                return

            try:
                idx = int(choice)
                if 1 <= idx <= len(topics):
                    # Single topic quiz
                    topic = topics[idx - 1]
                    cards = FlashcardContent.get_cards_for_topic(topic)
                    self._run_quiz(cards, topic.replace('_', ' ').title())
                elif idx == len(topics) + 1:
                    # Quick quiz
                    cards = FlashcardContent.get_random_cards(count=10)
                    self._run_quiz(cards, "Quick Quiz")
                elif idx == len(topics) + 2:
                    # Full quiz
                    cards = FlashcardContent.get_random_cards(count=100)
                    self._run_quiz(cards, "Full Quiz")
                else:
                    print(fmt.error("Invalid selection"))
                    input("Press Enter to continue...")
            except ValueError:
                print(fmt.error("Please enter a number or Q"))
                input("Press Enter to continue...")

    def _run_quiz(self, cards, quiz_name):
        """Run a flashcard quiz session."""
        if not cards:
            print(fmt.error("No flashcards available for this selection"))
            input("Press Enter to continue...")
            return

        self.correct = 0
        self.incorrect = 0
        self.skipped = 0

        random.shuffle(cards)

        fmt.clear_screen()
        fmt.print_header(f"FLASHCARD QUIZ: {quiz_name}")
        print(f"Cards: {len(cards)}")
        print()
        print("Controls:")
        print("  ENTER = Show answer")
        print("  Y = I knew it (correct)")
        print("  N = I didn't know (incorrect)")
        print("  H = Show hint")
        print("  S = Skip card")
        print("  Q = Quit quiz")
        print()
        input("Press Enter to start...")

        for i, card in enumerate(cards, 1):
            result = self._show_card(card, i, len(cards))
            if result == 'quit':
                break

        # Show results
        self._show_results(quiz_name)

    def _show_card(self, card, num, total):
        """Display a single flashcard and get response."""
        fmt.clear_screen()

        # Header with progress
        progress = f"Card {num}/{total}"
        score = f"Correct: {self.correct} | Incorrect: {self.incorrect}"
        print(f"{fmt.bold(progress)} | {score}")
        print("=" * 60)
        print()

        # Difficulty indicator
        diff = card['difficulty']
        diff_display = fmt.format_difficulty(diff) if hasattr(fmt, 'format_difficulty') else f"[{diff}]"
        print(f"Difficulty: {diff_display}")
        print()

        # Question
        print(fmt.bold("QUESTION:"))
        print()
        print(f"  {card['question']}")
        print()
        print("-" * 60)

        # Wait for user input
        while True:
            action = input("\n[Enter]=Answer [H]=Hint [S]=Skip [Q]=Quit: ").strip().lower()

            if action == 'h':
                print()
                print(fmt.warning(f"Hint: {card['hint']}"))
            elif action == 's':
                self.skipped += 1
                return 'skipped'
            elif action == 'q':
                return 'quit'
            elif action == '':
                break
            else:
                print("Invalid input. Press Enter for answer, H for hint, S to skip, Q to quit.")

        # Show answer
        print()
        print(fmt.bold("ANSWER:"))
        print()
        print(f"  {fmt.success(card['answer'])}")
        print()
        print("-" * 60)

        # Self-assessment
        while True:
            response = input("\nDid you know it? [Y]es / [N]o: ").strip().lower()

            if response in ['y', 'yes']:
                self.correct += 1
                print(fmt.success("Marked as correct!"))
                break
            elif response in ['n', 'no']:
                self.incorrect += 1
                print(fmt.error("Marked for review"))
                break
            else:
                print("Please enter Y or N")

        input("\nPress Enter for next card...")
        return 'continue'

    def _show_results(self, quiz_name):
        """Display quiz results."""
        fmt.clear_screen()
        fmt.print_header(f"QUIZ COMPLETE: {quiz_name}")

        total = self.correct + self.incorrect + self.skipped
        if total == 0:
            print("No cards answered.")
            input("\nPress Enter to continue...")
            return

        answered = self.correct + self.incorrect
        if answered > 0:
            accuracy = (self.correct / answered) * 100
        else:
            accuracy = 0

        print()
        print(fmt.bold("Results:"))
        print(f"  Total Cards: {total}")
        print(f"  {fmt.success('Correct')}: {self.correct}")
        print(f"  {fmt.error('Incorrect')}: {self.incorrect}")
        print(f"  Skipped: {self.skipped}")
        print()
        print(f"  Accuracy: {accuracy:.1f}%")
        print()

        # Performance feedback
        if accuracy >= 90:
            print(fmt.success("Excellent! You're exam-ready for this topic!"))
        elif accuracy >= 70:
            print(fmt.warning("Good job! A bit more review and you'll ace it."))
        elif accuracy >= 50:
            print(fmt.warning("Keep studying! Review the learning materials."))
        else:
            print(fmt.error("More practice needed. Try Learn Mode first."))

        print()
        input("Press Enter to continue...")


def run_flashcard_mode():
    """Run flashcard quiz mode (convenience function)."""
    mode = FlashcardMode()
    mode.start()
