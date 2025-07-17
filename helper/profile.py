class Profile():
    """Contains name weight RDI % preferences, ect. for user"""
    # Basal Metabolic Rate (BMR)
    ## (10 * weight (kg)) + (6.25 * height (cm)) - (5 * age) + 161 = kcal for resting a day
    ### For me that's about 1720 kcal a day

    # Total Energy Expenditure (TDEE)
    ## BMR * Activity Multiplier (AM)
    ### Lightly active AM = 1.375
    ### For me that's about 2365 kcal a day

    # For steady & healthy weightloss, remove roughtly 500 kcal from the daily kcal
    ## For me that's should be 1850 kcal a day