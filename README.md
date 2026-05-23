# canadian-credit-card-optimizer
# The Hidden Cost of a Canadian Credit Card

I have had the same credit card since university. I picked it because a friend had it and it seemed fine. I never actually calculated whether it was right for how I spend money.

When I moved from Waterloo to Mississauga everything changed. Groceries every week for the first time. Transit. Online shopping to set up a new apartment. Subscriptions. I realised I had no idea how much value I was leaving on the table every year by using the wrong card.

So I built the model to find out.

---

## What this is

A credit card rewards optimisation tool for Canadians. You enter your monthly spending across 8 categories and the app scores all 15 cards in the database, calculates the net annual value for each one based on your exact spending pattern, and ranks them in real time. It also compares three realistic Canadian spending profiles so you can see how the best card changes depending on how you spend.

The live app updates instantly as you adjust your spending sliders. No generic scores. Just the actual math for your situation.

---

## Live app

[Launch the Credit Card Optimizer](https://canadian-credit-card-optimizer-2026.streamlit.app/)

---

## What the analysis found

The gap between the best and worst card for a given spending profile is not small. For a recent grad the difference between the best and worst eligible card is $331 per year. For a young professional it is $543. For a dual income household it is $894. These are real dollars leaving the table every year simply because the card in the wallet is not matched to how that person actually spends.

| Profile | Best card | Net annual value | Gap vs worst card |
|---------|-----------|-----------------|-------------------|
| Recent Grad | Scotiabank Gold Amex | $348 per year | $331 per year |
| Young Professional | Scotiabank Gold Amex | $685 per year | $543 per year |
| Dual Income Household | Scotiabank Gold Amex | $1,223 per year | $894 per year |

The best no-fee card produces meaningful value too. The PC Financial World Elite Mastercard delivers $217 per year for a recent grad and $602 per year for a dual income household with no annual fee to recover.

Groceries are the single biggest rewards lever for most Canadians. A card with 5 or 6 percent on groceries applied to $500 per month generates $300 to $360 per year from that category alone before anything else is counted.

---

## How the scoring model works

For each card the model calculates gross annual rewards by applying the card's stated rate to your monthly spend in each category, then multiplying by 12. For cards with monthly spending caps the model applies the capped rate up to the limit and the base rate for any spend above the cap. The annual fee is subtracted to produce the net annual value.

This cap handling is something most comparison sites skip. A card advertising 5 percent on groceries with a $500 monthly cap performs very differently for someone spending $350 per month versus someone spending $900 per month. The model captures that correctly.

---

## Files in this repo

| File | What it is |
|------|-----------|
| app.py | The Streamlit app with four interactive tabs |
| card-database.csv | 15 Canadian credit cards with full rate, fee, and feature data |
| spending-profiles.csv | The three spending profiles used in the analysis |
| scoring-results.csv | Full ranking of all cards for all three profiles |
| category-impact.csv | Which spending categories drive the most rewards value per profile |
| summary-findings.csv | Headline findings across all three profiles |
| scoring-config.json | The category configuration used by the scoring engine |
| findings-report.pdf | Full analysis report with methodology, findings, and card comparisons |
| build-data.py | The Python script that built the dataset and ran the analysis |
| requirements.txt | Package dependencies for Streamlit Cloud |

---

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Data sources

Card rates, fees, and features were sourced from Ratehub.ca, Creditcardgenius.ca, and individual card issuer websites in May 2026. Rewards values are estimates based on stated card rates applied to the spending inputs. Actual rewards may vary based on card terms, category definitions, and spending behaviour.

---

## Skills this project demonstrates

Python financial modelling with category-level reward rate calculations and spending cap logic. Streamlit interactive app development and deployment. Comparative analysis across 15 financial products and 3 spending profiles. Requirements analysis — defining the scoring criteria and what net annual value actually means for different users. Data visualisation with Plotly. Business case writing in a financial services context.

---

## About this project

This is part of a portfolio series built while job searching in Canada after graduating from the University of Waterloo.

Prepared by Simran Saran. Targeting roles in business analysis, financial services, and data analysis across Canada.

This tool is for educational and comparison purposes and does not constitute financial advice.
