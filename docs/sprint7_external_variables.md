# Sprint 7 — External Variables and SARIMAX

## 1. Objective

The objective of Sprint 7 was to investigate whether an external economic
variable could improve forecasting of India's Food Products IIP.

The selected external variable was All-India General Consumer Price Index
(CPI), Combined sector, Base 2012=100.

---

## 2. CPI Dataset

Source:
Ministry of Statistics and Programme Implementation (MoSPI)

Series:
All India General CPI — Combined

Base year:
2012=100

Period:
January 2013 to March 2025

Observations:
147 monthly observations

Validation:

- 147 rows
- No missing CPI values
- No duplicate dates
- No missing months
- Start date: January 2013
- End date: March 2025

---

## 3. IIP–CPI Alignment

The original Food Products IIP dataset covers:

April 2012 to March 2025

The CPI series begins in January 2013.

Therefore, the common period used for the external-variable experiment was:

January 2013 to March 2025

Total aligned observations:

147

The IIP target variable contained no missing values in the aligned
dataset.

The single missing value in the IIP growth_rate column was retained because
growth_rate was not used as the forecasting target or primary exogenous
variable.

Output:

data/processed/iip_food_products_with_cpi_2013_2025.csv

---

## 4. CPI Stationarity

ADF test on CPI level:

- ADF statistic: 1.918409
- p-value: 0.998557

Conclusion:

The CPI level was non-stationary at the 5% significance level.

ADF test after first differencing:

- ADF statistic: -3.048292
- p-value: 0.030624

Conclusion:

The first-differenced CPI series was stationary at the 5% significance
level.

---

## 5. Final Test Split

For the aligned dataset:

Training period:

January 2013 to March 2024

Training observations:

135

Final test period:

April 2024 to March 2025

Test observations:

12

Leakage checks passed:

- Training ends before test period
- No training/test date overlap
- Test contains 12 observations
- No missing CPI values in training
- No missing CPI values in test

---

## 6. Ex-Post SARIMAX Experiment

A SARIMAX model with the same SARIMA structure used in the research paper
was fitted:

SARIMA component:

(1,1,1)(1,1,1,12)

Exogenous variable:

CPI General Combined

The realized CPI values from the test period were supplied to the model.

Results:

- MAE: 5.259865
- RMSE: 6.845576
- MAPE: 3.979323%
- AIC: 708.018899
- BIC: 724.111686

This was treated as an ex-post diagnostic experiment because realized
future CPI values would not normally be known at the beginning of the
forecast horizon.

Therefore, these results are not treated as the production forecasting
result.

---

## 7. Realistic Walk-Forward Experiment

To avoid using realized future CPI, CPI was first forecast using an
additive Holt-Winters/Triple Exponential Smoothing model.

The resulting CPI forecasts were then supplied to SARIMAX.

Forecast structure:

Historical CPI
    ↓
CPI forecast
    ↓
Forecasted CPI supplied to SARIMAX
    ↓
Food Products IIP forecast

---

## 8. Matched Walk-Forward Comparison

The comparison used identical forecast origins and 12-month horizons for
both SARIMA and SARIMAX.

Valid origins:

- 96 observations
- 108 observations
- 120 observations

A fourth origin was not used because the development dataset ended in
March 2024 and did not contain 12 subsequent observations after origin
132.

### Average Results

| Model | Average MAE | Average RMSE | Average MAPE |
|---|---:|---:|---:|
| SARIMA | 4.527495 | 6.004163 | 3.494651% |
| SARIMAX + Forecasted CPI | 4.424115 | 5.838509 | 3.400661% |

The SARIMAX configuration with forecasted CPI produced slightly lower
average MAE, RMSE, and MAPE across the three matched walk-forward origins.

Approximate reductions relative to SARIMA:

- MAE: 2.28%
- RMSE: 2.76%
- MAPE: 2.69%

---

## 9. Interpretation

The results provide evidence that incorporating forecasted CPI as an
external variable can provide a modest predictive improvement for the
Food Products IIP series in the three matched walk-forward experiments.

However, the improvement is relatively small and is not consistent in
magnitude across all forecast origins.

Therefore, CPI should be treated as a candidate external predictor rather
than a universally useful variable.

The experiment does not establish a causal relationship between CPI and
industrial production.

---

## 10. Limitations

1. The CPI series begins in January 2013, reducing the common sample from
   156 IIP observations to 147 observations.

2. Only three valid 12-month walk-forward origins were available for the
   matched CPI experiment.

3. Future CPI was itself forecast using Holt-Winters, introducing a
   second-stage forecasting dependency.

4. The ex-post experiment used realized future CPI and therefore should
   not be interpreted as a deployable forecasting configuration.

5. CPI is only one potential external variable. Other variables such as
   rainfall, temperature, energy prices, economic indicators, and calendar
   variables may contain additional predictive information.

6. The observed predictive association does not establish causality.

---

## 11. Sprint 7 Conclusion

Sprint 7 successfully established an external-variable forecasting
pipeline using CPI.

The realistic walk-forward experiment showed a modest reduction in average
forecasting error when forecasted CPI was incorporated into SARIMAX.

The result supports retaining CPI as a candidate feature in the broader
forecasting system, while avoiding the claim that CPI is universally
beneficial.

The project should therefore continue to evaluate additional external
variables and machine-learning models using the same time-series
validation principles.