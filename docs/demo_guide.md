# Demo Guide

Comprehensive guide for presenting the Carbon Market Intelligence platform (3-5 minute demo).

## Pre-Demo Checklist

### 1 Day Before Demo
- [ ] Run all tests: `python run_tests.py`
- [ ] Verify backend starts: `python run_backend.py`
- [ ] Install frontend dependencies: `cd frontend && npm install`
- [ ] Verify frontend starts: `npm run dev`
- [ ] Test all tabs and features
- [ ] Prepare backup screenshots/video
- [ ] Practice demo flow 2-3 times

### 1 Hour Before Demo
- [ ] Start backend: `python run_backend.py`
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Open browser to `http://localhost:3000`
- [ ] Verify all tabs load correctly
- [ ] Have API docs ready: `http://localhost:8000/docs`
- [ ] Close unnecessary applications
- [ ] Disable notifications

### Just Before Demo
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Browser open to dashboard
- [ ] Zoom level comfortable for audience
- [ ] Clear browser console

## Demo Script (3-5 Minutes)

### Opening (30 seconds)

**Script:**
> "I'm presenting the Carbon Market Intelligence platform - a comprehensive solution for analyzing and predicting global carbon credit markets using machine learning and data analytics.
>
> The problem we're solving: Carbon markets are complex, with 223 countries, volatile pricing, and limited forecasting tools. Companies and investors need intelligence to make informed decisions.
>
> Our solution combines 20 years of historical data, ML models, country risk scoring, and interactive scenario simulation into one platform."

**Actions:**
- Show dashboard landing page
- Highlight the four main tabs

### Section 1: Global Market Intelligence (60 seconds)

**Script:**
> "Let's start with Global Market Analysis. Here we see real-time KPIs showing the latest market value of $535 million and volume of 84 million tons of CO2 in 2024.
>
> The year-over-year changes show the market dynamics - you can see the decline from the 2021 peak.
>
> Below, we have interactive charts powered by Plotly showing 20 years of historical data from 2005 to 2024, plus ML-generated forecasts for the next 3 years.
>
> Our forecasting uses walk-forward cross-validation - we compared naive baselines against XGBoost and Random Forest models. For market volume, XGBoost performed best with an RMSE of 172, while for value, the naive baseline actually outperformed ML due to the structural break in 2021."

**Actions:**
- Point to KPI cards (latest value, volume)
- Point to YoY changes
- Scroll to show both charts (Value and Volume)
- Hover over data points to show tooltips
- Point to forecast portion (dashed line)

**Key Visual**: The 2021 spike in the charts

### Section 2: Country Intelligence (60 seconds)

**Script:**
> "Next, Country Intelligence. We've scored 223 countries on both risk and opportunity.
>
> The risk ranking identifies high-emission countries with weak climate policies - Saudi Arabia tops the list with a risk score of 86.82, driven by high per-capita emissions and weak renewable adoption.
>
> Switching to opportunities, Costa Rica leads with 83.13, thanks to 99% renewable electricity and strong GDP growth.
>
> You can search for any country - let's look at China. We see detailed metrics: 11.5 billion tons of CO2, a growing renewable sector at 28.5%, and both risk and opportunity scores."

**Actions:**
- Click "Country Intelligence" tab
- Show risk ranking table (Saudi Arabia #1)
- Click "Opportunity Ranking" button
- Show opportunity table (Costa Rica #1)
- Use search box to find "China"
- Click "View Details" for China
- Show the detailed country profile

**Key Visual**: Risk vs Opportunity comparison

### Section 3: Trading Prediction (45 seconds)

**Script:**
> "For companies, we provide trading recommendations. Our ML classifier predicts whether a company should Buy or Sell carbon credits based on 8 pre-decision features.
>
> The model uses Logistic Regression trained on 5,000 transactions, achieving an F1 score of 0.54 - better than random but indicating this is a challenging prediction task.
>
> Let me show a prediction: An energy company using coal with an emissions deficit of 500 tons. The model predicts 'Sell' with medium confidence, suggesting they should sell existing credits rather than buy more."

**Actions:**
- Click "Trading Prediction" tab
- Show model info card (F1: 0.54)
- Point to pre-filled form fields
- Click "Predict Trading Action"
- Show result (Buy/Sell with confidence)
- Point to probability and input summary

**Key Visual**: The prediction result card

### Section 4: Scenario Simulator (60 seconds)

**Script:**
> "Finally, our scenario simulator. This is where users can explore what-if questions.
>
> We have three quick scenarios: Green Transition, Economic Boom, and Carbon Tax. Let's try Green Transition - 30% more renewables, 15% fewer emissions, 5% GDP growth.
>
> The simulation runs instantly, comparing baseline predictions against the scenario. Here we see market volume could increase by over 300% while value stays flat - that's because our value model uses a simple baseline while volume uses XGBoost which responds to renewable energy changes.
>
> The warnings at the bottom explain interpretation - this is scenario analysis, not guaranteed forecasting."

**Actions:**
- Click "Scenario Simulator" tab
- Click "Green Transition" quick scenario
- Show sliders adjusting
- Click "Run Simulation"
- Show results (baseline vs scenario)
- Point to the volume change (+305%)
- Show warnings section

**Key Visual**: The dramatic volume change visualization

### Technical Highlight (30 seconds)

**Script:**
> "Under the hood, this is a full-stack application: React frontend with Tailwind and Plotly, FastAPI backend with Pydantic validation, and machine learning with scikit-learn and XGBoost.
>
> All models were trained with proper validation - walk-forward for time series, stratified splits for classification, and careful leakage prevention.
>
> The API is fully documented with OpenAPI - here's the Swagger UI showing all 12 endpoints."

**Actions:**
- Open new tab: `http://localhost:8000/docs`
- Show OpenAPI documentation
- Expand one endpoint (e.g., /api/market/overview)
- Show the "Try it out" feature

**Key Visual**: OpenAPI documentation

### Closing (30 seconds)

**Script:**
> "In summary, we've built a comprehensive carbon market intelligence platform that:
> - Forecasts market trends using validated ML models
> - Scores 223 countries on risk and opportunity
> - Provides company-level trading recommendations
> - Enables interactive scenario analysis
>
> The platform is production-ready with complete testing, API documentation, and a professional UI.
>
> All code is on GitHub, fully documented, and tested. Thank you!"

**Actions:**
- Switch back to dashboard
- Briefly show each tab again
- End on the Global Market tab

## Demo Tips

### Do's
✓ **Practice timing** - Run through 2-3 times before demo
✓ **Use the tab key** - Faster than mouse for form navigation
✓ **Speak to the value** - Emphasize business impact, not just features
✓ **Show, don't tell** - Let visuals speak when possible
✓ **Highlight ML rigor** - Mention validation, leakage prevention
✓ **Be honest about limitations** - F1 of 0.54, small dataset size
✓ **Have backup plan** - Screenshots/video if live demo fails

### Don'ts
✗ **Don't apologize for limitations** - State them as facts
✗ **Don't debug live** - Skip to next feature if something breaks
✗ **Don't rush** - Speak clearly and at moderate pace
✗ **Don't over-explain** - Save technical details for Q&A
✗ **Don't forget to breathe** - Pause between sections

## Q&A Preparation

### Expected Questions

**Q: How accurate are your predictions?**
A: "Our market volume model has an RMSE of 172 on walk-forward validation. The trading classifier achieves F1 of 0.54, indicating this is a difficult task - market dynamics involve many factors beyond our features. We're transparent about these metrics rather than claiming unrealistic accuracy."

**Q: Where does your data come from?**
A: "We use five authoritative sources: voluntary carbon market statistics, Global Carbon Budget emissions data, World Bank renewable energy and GDP data, and OECD carbon pricing. All processed datasets are in the repository with full provenance."

**Q: How does the scenario simulator work?**
A: "It modifies the input features to our trained models based on your parameters. For example, increasing renewable share by 30% adjusts the Renewable_Electricity_Share_lag1 feature, then re-runs the XGBoost model. It's scenario analysis showing directional impact, not causal forecasting."

**Q: Why is the trading model accuracy so low?**
A: "F1 of 0.54 is only slightly better than random, which reflects the genuine difficulty of this prediction task. Real trading decisions involve proprietary strategies, market timing, and external factors not in our dataset. We included this to be realistic about ML capabilities."

**Q: Can you add real-time data?**
A: "Yes, the architecture supports it. We'd need API connections to live market feeds, a database for streaming data, and model retraining pipeline. The current version uses static 2005-2024 data as a proof of concept."

**Q: How long did this take to build?**
A: "Phase 3 (ML) was already complete. I built Phase 4 through 9 - backend API, frontend dashboard, integration, testing, and documentation - in [X hours]. The modular architecture and clear requirements enabled rapid development."

**Q: Is this deployable?**
A: "Yes, it's production-ready for internal use. For public deployment we'd add authentication, migrate to a database, set up CI/CD, containerize with Docker, and deploy to cloud (AWS/Azure/GCP). The architecture supports scaling horizontally."

## Alternative Demo Flows

### For Technical Audience (5 minutes)
1. Quick feature tour (1 min)
2. Architecture deep-dive (2 min)
   - Show system diagram
   - Explain ML validation strategy
   - Discuss data pipeline
3. API demonstration (1 min)
   - OpenAPI docs
   - Show curl example
4. Code walkthrough (1 min)
   - Backend structure
   - Model loading
   - Frontend components

### For Business Audience (3 minutes)
1. Problem statement (30 sec)
2. Market intelligence value (1 min)
3. Country intelligence value (1 min)
4. Scenario analysis value (30 sec)
5. Closing with ROI potential

### For Judges (4 minutes)
1. Quick overview (30 sec)
2. Technical innovation (1 min)
   - ML validation rigor
   - Leakage prevention
   - Full-stack integration
3. Feature demonstration (1.5 min)
   - One feature from each section
4. Completeness (30 sec)
   - Testing, documentation, deployability
5. Future potential (30 sec)

## Backup Materials

### If Live Demo Fails
Have ready:
1. **Screenshots** of each major feature
2. **Video recording** of full demo
3. **Postman collection** for API demonstration
4. **Jupyter notebook** showing model training

### If Questions Go Deep
Have open in background tabs:
1. `docs/architecture.md`
2. `docs/phase3_results.md`
3. `ml/training/global_market_model.py`
4. `docs/scenario_simulator.md`

## Time Management

- **3-minute version**: Skip Technical Highlight, brief Q&A
- **5-minute version**: Full script above
- **7-minute version**: Add architecture diagram, code snippets
- **10-minute version**: Live API calls, detailed model explanation

## Common Demo Mistakes to Avoid

1. **Starting with architecture** - Lead with value/features
2. **Over-explaining the obvious** - Trust audience to see UI
3. **Ignoring the clock** - Have a watch/timer visible
4. **Reading slides** - You don't have slides, speak naturally
5. **Apologizing for bugs** - State limitations confidently
6. **Forgetting the story** - Connect features to problem
7. **Going too fast** - Pause after each major section

## Post-Demo Actions

After successful demo:
- [ ] Export demo video
- [ ] Save judge feedback
- [ ] Update README with demo link
- [ ] Create GitHub release
- [ ] Write blog post (optional)
- [ ] Share on LinkedIn (optional)

## Troubleshooting During Demo

### Backend won't start
→ Show API documentation screenshots
→ Run `python test_backend.py` to prove it works
→ Use backup video

### Frontend won't load
→ Show OpenAPI docs and make live API calls
→ Explain the architecture
→ Use screenshots

### Chart won't render
→ Describe what it would show
→ Show raw data in table
→ Move to next feature quickly

### Prediction takes too long
→ Explain it's running ML inference
→ Show model metrics while waiting
→ Prepare with pre-computed example

## Success Metrics

A successful demo:
- ✓ Delivers key message in time limit
- ✓ Shows all four major features
- ✓ Demonstrates technical competence
- ✓ Handles questions confidently
- ✓ Leaves audience wanting to learn more

## Final Checklist

Before walking into demo:
- [ ] Application running smoothly
- [ ] Browser tabs organized
- [ ] Backup materials ready
- [ ] Timer started
- [ ] Confidence high
- [ ] Ready to impress!

Good luck! 🚀
