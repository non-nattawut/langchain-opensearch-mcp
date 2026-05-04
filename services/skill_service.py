class SkillService:
    @staticmethod
    def load_skills():
        try:
            with open("skills.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a helpful assistant."