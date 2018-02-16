from . import lifecycle


CHECKS_TO_RUN = [
    'procenv.checks.ProcfileCheck',
    'procenv.checks.PortBindCheck',
    'procenv.checks.DatabaseURLCheck',
    'procenv.checks.RedisURLCheck',
]


def main():
    lifecycle.start(checks=CHECKS_TO_RUN)

if __name__ == '__main__':
    main()
