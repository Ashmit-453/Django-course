1. Q OBJECT QUERIES
a. Restaurants with Italian OR Mexican cuisine:

--- Italian/Mexican Restaurants ---
Count: 4
  • Mario's Italian Kitchen (Italian) - Opened: 2025-08-02
  • Taco Bell Express (Mexican) - Opened: 2025-09-01
  • Pizza Palace 123 (Italian) - Opened: 2025-09-06
  • Cinco de Mayo Restaurant (Mexican) - Opened: 2025-07-18

SQL Generated:
  SELECT "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_restaurant" WHERE ("restaurant_restaurant"."restaurant_type" = 'italian' OR "restaurant_restaurant"."restaurant_type" = 'mexican')


b. Restaurants NOT opened in the last 30 days:

--- Not Recently Opened ---
Count: 6
  • Mario's Italian Kitchen (Italian) - Opened: 2025-08-02
  • The Sports Grill (American) - Opened: 2025-05-19
  • Sunset Cafe (American) - Opened: 2025-02-28
  • Dragon Wok (Chinese) - Opened: 2025-06-28
  • Le Petit Cafe (French) - Opened: 2024-11-20
  • Cinco de Mayo Restaurant (Mexican) - Opened: 2025-07-18

SQL Generated:
  SELECT "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_restaurant" WHERE NOT ("restaurant_restaurant"."date_opened" >= '2025-08-17')


c. Italian/Mexican OR opened in last 30 days:

--- Combined Condition ---
Count: 6
  • Mario's Italian Kitchen (Italian) - Opened: 2025-08-02
  • Taco Bell Express (Mexican) - Opened: 2025-09-01
  • Pizza Palace 123 (Italian) - Opened: 2025-09-06
  • Mumbai Spice House (Indian) - Opened: 2025-08-22
  • Burger Grill 24/7 (American) - Opened: 2025-09-11
  • Cinco de Mayo Restaurant (Mexican) - Opened: 2025-07-18

SQL Generated:
  SELECT "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_restaurant" WHERE ("restaurant_restaurant"."restaurant_type" = 'italian' OR "restaurant_restaurant"."restaurant_type" = 'mexican' OR "restaurant_restaurant"."date_opened" >= '2025-08-17')


2. PATTERN MATCHING LOOKUPS
a. Restaurants with "grill" in name (case-insensitive):

--- Grill Restaurants ---
Count: 2
  • The Sports Grill (American) - Opened: 2025-05-19
  • Burger Grill 24/7 (American) - Opened: 2025-09-11

SQL Generated:
  SELECT "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_restaurant" WHERE "restaurant_restaurant"."name" LIKE '%grill%' ESCAPE '\'


b. Restaurants ending with "Cafe":

--- Cafe Restaurants ---
Count: 2
  • Sunset Cafe (American) - Opened: 2025-02-28
  • Le Petit Cafe (French) - Opened: 2024-11-20

SQL Generated:
  SELECT "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_restaurant" WHERE "restaurant_restaurant"."name" LIKE '%Cafe' ESCAPE '\'


3. REGEX LOOKUPS
a. Restaurants with digits in name:

--- Restaurants with Digits ---
Count: 2
  • Pizza Palace 123 (Italian) - Opened: 2025-09-06
  • Burger Grill 24/7 (American) - Opened: 2025-09-11

SQL Generated:
  SELECT "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_restaurant" WHERE "restaurant_restaurant"."name" REGEXP '[0-9]+'


b. Profitable sales OR restaurant name has digits:
Retrieve all Sale records where income is greater than expenditure OR the associated restaurant's name contains any digit (combine Q objects and regex).

--- Complex Sales Query ---
Count: 5
  • Mario's Italian Kitchen: Income $5000.00, Expenditure $3000.00 (Profit)
  • The Sports Grill: Income $8000.00, Expenditure $4000.00 (Profit)
  • Pizza Palace 123: Income $6000.00, Expenditure $3500.00 (Profit)
  • Pizza Palace 123: Income $3000.00, Expenditure $4000.00 (Loss)
  • Burger Grill 24/7: Income $3000.00, Expenditure $4000.00 (Loss)

SQL Generated (1 queries):
  Query 1: SELECT "restaurant_sale"."id", "restaurant_sale"."restaurant_id", "restaurant_sale"."income", "restaurant_sale"."expenditure", "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_sale" INNER JOIN "restaurant_restaurant" ON ("restaurant_sale"."restaurant_id" = "restaurant_restaurant"."id") WHERE ("restaurant_sale"."income" > ("restaurant_sale"."expenditure") OR "restaurant_restaurant"."name" REGEXP '[0-9]+')


4. COMPLEX COMBINED QUERIES WITH OPTIMIZATION
Complex query with select_related optimization:
Use select_related('restaurant') when querying Sale to minimize database hits.

Count: 5
  • Mario's Italian Kitchen: Income $5000.00, Expenditure $3000.00 (Profit)
  • Taco Bell Express: Income $2000.00, Expenditure $2500.00 (Loss)
  • Pizza Palace 123: Income $6000.00, Expenditure $3500.00 (Profit)
  • Pizza Palace 123: Income $3000.00, Expenditure $4000.00 (Loss)
  • Burger Grill 24/7: Income $3000.00, Expenditure $4000.00 (Loss)

SQL Generated (1 queries):
  Query 1: SELECT DISTINCT "restaurant_sale"."id", "restaurant_sale"."restaurant_id", "restaurant_sale"."income", "restaurant_sale"."expenditure", "restaurant_restaurant"."id", "restaurant_restaurant"."name", "restaurant_restaurant"."restaurant_type", "restaurant_restaurant"."date_opened" FROM "restaurant_sale" INNER JOIN "restaurant_restaurant" ON ("restaurant_sale"."restaurant_id" = "restaurant_restaurant"."id") WHERE ("restaurant_restaurant"."restaurant_type" IN ('italian', 'mexican') OR "restaurant_restaurant"."date_opened" >= '2025-08-17')