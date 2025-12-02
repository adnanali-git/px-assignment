
class SwitchValues:
    # could be moved to .env file at first thought but upon further thinking 
    # one realises that it doesn't matter since this variable is only due to
    # the simulation/mocking requirement in this task. It doesn't arise in a
    # real-life production codebase.
    IS_MOCKING_VIA_FILE: bool = True 