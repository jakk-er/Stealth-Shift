banner_displayed = False

def display_banner():
    global banner_displayed
    if not banner_displayed:
        banner = """
=========================================================================
====                                                                 ====
====  @@@@@@  @@@@@@@  @@@@@@@@   @@@@@@   @@@    @@@@@@@  @@@  @@@  ====
==== !@@        @@!    @@!       @@!  @@@  @@!      @@!    @@!  @@@  ====
==== !!@@!!     @!!    @!!!:!    @!@!@!@!  @!!      @!!    @!@!@!@!  ====
====  !!@!!!    !!!    !!!!!:    !!!  !!!  !!!      !!!    !!!  !!!  ====
====      !:!   !!:    !!:       !!:  !!!  !!:      !!:    !!   !!!  ====
==== :::: ::     ::     :: ::::  ::   :::   :: ::::  ::    ::   :::  ====
====                                                                 ====   
====                                                                 ====   
====  @@@@@@  @@@  @@@  @@@  @@@@@@@@  @@@@@@@                       ====
==== !@@      @@!  @@@  @@!  @@!         @@!                         ====
==== !!@@!!   @!@!@!@!  !!@  @!!!:!      @!!       STEALTH SHIFT     ====
====  !!@!!!  !!!  !!!  !!!  !!!         !!!           v 1.0         ====
====      !:! !!   !!!  !!:  !!          !!:                         ====
==== :::: ::  ::   :::   ::  ::           ::         by Jakk-er      ====
====                                                                 ====
=========================================================================
              \n \n"""
        print(banner)
        banner_displayed = True

if __name__ == "__main__":
    display_banner()
