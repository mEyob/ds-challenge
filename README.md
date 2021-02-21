### Table of Contents
1. [Introduction](README.md#introduction)
1. [What is the structure of the data in the data set?](README.md#What-is-the-structure-of-the-data-in-the-data-set?)
1. [Do any columns in the data set make the most sense to be encoded into labels for better statistical analysis?](README.md#Do-any-columns-in-the-data-set-make-the-most-sense-to-be-encoded-into-labels-for-better-statistical-analysis?)
1. [Are there any obvious outliers or invalid/empty values in the labeled data set?](README.md#Are-there-any-obvious-outliers-or-invalid/empty-values-in-the-labeled-data-set?)
1. [What are the most expensive parts? What is the price distribution?](README.md#What-are-the-most-expensive-parts?-What-is-the-price-distribution?)
1. [Which departments are spending the most money?](README.md#Which-departments-are-spending-the-most-money?)
1. [Which zip code has the most supplier concentration? Any idea why?](README.md#Which-zip-code-has-the-most-supplier-concentration?-Any-idea-why?)
1. [What are the top UNSPSC categories?](README.md#What-are-the-top-UNSPSC-categories?)
1. [If you could spend another day cleaning up the data to make it more useful what might you do?](README.md#If-you-could-spend-another-day-cleaning-up-the-data-to-make-it-more-useful-what-might-you-do?)
1. [If you could find another data set that would complement this one to help answer the above or similar questions, what dataset might be ideal?](README.md#If-you-could-find-another-data-set-that-would-complement-this-one-to-help-answer-the-above-or-similar-questions,-what-dataset-might-be-ideal?)


##### Introduction
This repository analyzes records of Purchase Order data made publicly available by California state.

##### What is the structure of the data in the data set?
The dataset contains
- It contains $346018$ rows of purchase orders with $31$ columns. 
- The datatypes of all columns, as inferred by Pandas, is either object or float64.

```python
df.columns
```
<center><img src="img/columns.png" align="middle" style="width: 400px; height: 150px" /></center><br>

- Some of the inferred datatypes (e.g. for *Unit Price* and *Total Price* columns) are incorrect, so they need to be converted to the appropriate data type before we can start analyzing the data.

```python
df["Total Price Numeric"] = df["Total Price"].apply(to_float)
df["Unit Price Numeric"] = df["Unit Price"].apply(to_float)
```

##### Do any columns in the data set make the most sense to be encoded into labels for better statistical analysis?

Nominal and ordinal data types can be encoded into labels for better statistical analysis and model building.

For example, the *Acquisition Method* is a nominal data with the following unique values

```python
df["Acquisition Method"].unique()
```

<center><img src="img/acquisition-method.png" align="middle" style="width: 400px; height: 150px" /></center><br>

Let us create a simple bar plot of aggregate *Total Spend* per *Acuisition Method*

```python
spend_by_aq_method = df.groupby("Acquisition Method", as_index=False)\
                       .agg(number_of_purchases=("Total Price Numeric", "count"), \
                         total_spend=("Total Price Numeric", "sum"))\
                       .sort_values("total_spend", ascending=False)
```
```python
spend_by_aq_method.plot.bar(x="Acquisition Method", y="total_spend")
```

<center><img src="img/spend-by-aq-method.png" align="middle" style="width: 400px; height: 500px" /></center><br>

The above plot shows most of the purchases are done under the "Informal Competitive", "Services are specifically exempt by statute", "Formal Competitive", and "Services are specifically exempt by policy" acquisition methods respectively.

However, the plot looks busy and is hard to read. Encoding the acquisition method makes it cleaner.

Other columns that may benefit from label encoding:
- Acquisition Type
- Sub-Acquisition Type
- Sub-Acquisition Method

##### Are there any obvious outliers or invalid/empty values in the labeled data set?

Most of the columns have missing values. Most notably, the *Requisition Number* and *Sub-Acquisition Method* columns have 331649 ($95.8\%$ of the rows) and 315122 ($91\%$) missing values

If we label-encode the *Sub-Acquisition Method* Column, there will be $315122$ **invalid** codes with value $-1$, which corresponds to the NULL values in the column

<center><img src="img/sub-aq-category.png" align="middle" style="width: 500px; height: 400px" /></center><br>

##### What are the most expensive parts? What is the price distribution?

The top ten most expensive items are

```python
df.loc[df["Unit Price"].notna(), ["Item Name", "Unit Price Numeric"]]\
  .sort_values("Unit Price Numeric", ascending=False).head(10)
```

<center><img src="img/top-10-expensive.png" align="middle" style="width: 400px; height: 300px" /></center><br>

Two things become obvious from the price distribution

<center><img src="img/describe-price.png" align="middle" style="width: 400px; height: 400px" /></center><br>

1. there are some *invalid* values in the *Unit Price Numeric* & *Total Price Numeric* columns since prices cannot be negative.

```python
df.loc[df["Total Price Numeric"] < 0].shape

(1438, 35)
```

2. It is also easy to see that there are outliers in these columns. The following cell illustrate this point

```python
IQR = df["Total Price Numeric"].quantile(0.75) - df["Total Price Numeric"].quantile(0.25) 
df[df["Total Price Numeric"] > 3*IQR].shape

(45294, 35)
```

If we cut-off the maximum price at $\$100,000$, we'll get the following price distribution

```python
expensive_items = df["Total Price Numeric"] > 1e5 # Roughly 92 percentile
invalid_item_price = df["Total Price Numeric"] < 0
total_price_hist = df.loc[(~expensive_items) & (~invalid_item_price), "Total Price Numeric"].plot(kind="hist", bins=20, ec='black')
total_price_hist.set_xlabel("Total Price ($)")
```

<center><img src="img/price-hist.png" align="middle" style="width: 600px; height: 300px" /></center><br>

About half of the purchases are cheaper than $\$5000$ dollars, and about $90\%$ of the purchases are less than $\$100,000$

##### How has Purchase Order spend been trending over time?

```python
df["Creation Year"] = pd.to_datetime(df["Creation Date"]).dt.to_period('Y')
valid_price = df["Total Price Numeric"] >= 0

spend_trend = df[valid_price].groupby("Creation Year", as_index=False).agg(Spend=("Total Price Numeric", "sum"))
```
<center><img src="img/spend-by-year.png" align="middle" style="width: 400px; height: 300px" /></center><br>

In general, the spending trend over the years has been growing. The spike in 2013 is the result of a few high-dollar spends whose actual purchase date backdates the creation date.

##### Which departments are spending the most money?

##### Which zip code has the most supplier concentration? Any idea why?

##### What are the top UNSPSC categories? 

##### If you could spend another day cleaning up the data to make it more useful what might you do?

##### If you could find another data set that would complement this one to help answer the above or similar questions, what dataset might be ideal?