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

    # Macro ratio for fat loss and muscle tone are 30%, 30%, 40% (Protein, fat, carb) of kcal
    # Fat loss (30-35), (25-30), (35-40)
    # Muscle gain (25-30), (20-25), (45-55)
    # Balanced (25-30), (25-30), (40-50)
    # Keto (15-20), (60-70), (5-10)

    # Macronutrient targets for me:
    ## Fiber = 30g
    ## Iron = 18mg (maybe more since I'm taking iron pills to help iron deficancy)
    ## Calcium = 1200mg
    ## Magnesium = 350mg
    ## Potassium = 2900mg
    ## Vitamin D = 1000IU
    ## Vitamin C = 90mg (less if not stressed (75mg))

    # Under 25g of sugar a day, aim for 10-20g a day