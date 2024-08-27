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
==== !!@@!!   @!@!@!@!  !!@  @!!!:!      @!!                         ====
====  !!@!!!  !!!  !!!  !!!  !!!         !!!                         ====
====      !:! !!   !!!  !!:  !!          !!:         by Jakk-er      ====
==== :::: ::  ::   :::   ::  ::           ::                         ====
====                                                                 ====
=========================================================================
              \n \n"""
        print(banner)
        banner_displayed = True

if __name__ == "__main__":
    display_banner()
