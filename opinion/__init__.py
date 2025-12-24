from otree.api import *

doc = """
1. Collect opinions
2. Ask for a motivation for one opinion
"""

class Constants(BaseConstants):
    name_in_url = 'opinion'
    players_per_group = None
    num_rounds = 1
    max_chars = 500 # maximum number of characters for motivation


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

#just a few examples
statements = [
    "The government should do more to reduce inequality.",
    "People can generally be trusted.",
    "There should be an annual upper limit to the uptake of new asylum seekers.",
    "Climate change policies should be prioritized even if they cost jobs.",
]

# index of the opinion for which we ask participants to give a motivation
# this may be drawn randomly
statement_id = 3

scale_choices = [(i, str(i)) for i in range(-10, 11)]

def make_field(statement):
    return models.IntegerField(
        choices=scale_choices,
        widget=widgets.RadioSelect,
        label=statement,
    )

class Player(BasePlayer):
    motivation = models.LongStringField(
        label=f"Please explain why you chose this answer (max {Constants.max_chars} characters)."
    )

for idx, stmt in enumerate(statements, start=1):
    setattr(Player, f"s{idx}", make_field(stmt))

# PAGES
class Opinions(Page):
    form_model = "player"
    form_fields = [f"s{i}" for i in range(1, len(statements) + 1)]

class Motivation(Page):
    form_model = "player"
    form_fields = ["motivation"]

    @staticmethod
    def vars_for_template(player: Player):
        stmt = statements[statement_id - 1]
        answer = getattr(player, f"s{statement_id}")
        return dict(
            statement=stmt,
            answer=answer,
            max_chars=Constants.max_chars
        )

    @staticmethod
    def error_message(player: Player, values):
        text = (values.get("motivation") or "").strip()

        if not text:
            return "Please provide an argumentation."

        char_count = len(text)
        if char_count > Constants.max_chars:
            return (
                f"Please keep your argumentation to "
                f"{Constants.max_chars} characters or fewer "
                f"(currently {char_count})."
            )

    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        player.participant.vars["statement_id"] = statement_id
        player.participant.vars["statement"] = statements[statement_id - 1]
        player.participant.vars["opinion"] = getattr(player, f"s{statement_id}")
        player.participant.vars["motivation"] = (player.motivation or "").strip()


page_sequence = [Opinions, Motivation]
