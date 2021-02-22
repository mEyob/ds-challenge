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
1. [Future work](README.md#Future-work)

### Introduction
This repository analyzes a collection of publicly available records of Purchase Order data from the state of California.

### What is the structure of the data in the data set?
- The dataset contains 346018 rows of purchase orders with 31 columns listed below.
```python
df.shape

# Output
(346018, 31)
```
```python
df.columns

# Output
Index(['Creation Date', 'Purchase Date', 'Fiscal Year', 'LPA Number',
       'Purchase Order Number', 'Requisition Number', 'Acquisition Type',
       'Sub-Acquisition Type', 'Acquisition Method', 'Sub-Acquisition Method',
       'Department Name', 'Supplier Code', 'Supplier Name',
       'Supplier Qualifications', 'Supplier Zip Code', 'CalCard', 'Item Name',
       'Item Description', 'Quantity', 'Unit Price', 'Total Price',
       'Classification Codes', 'Normalized UNSPSC', 'Commodity Title', 'Class',
       'Class Title', 'Family', 'Family Title', 'Segment', 'Segment Title',
       'Location'],
      dtype='object')
```
- Some of the columns have missing values. For example, as shown below, the Purchase Date column has 17436 missing values.

```python
df.isna().sum()

# Output
Creation Date                      0
Purchase Date                  17436
Fiscal Year                        0
LPA Number                    253673
Purchase Order Number              0
Requisition Number            331649
Acquisition Type                   0
Sub-Acquisition Type          277681
Acquisition Method                 0
Sub-Acquisition Method        315122
                ...
```
- Some of the inferred datatypes (e.g. for *Unit Price* and *Total Price* columns) are incorrect, so they need to be converted to the appropriate data type before we can start analyzing the data.

```python
df["Total Price Numeric"] = df["Total Price"].apply(to_float)
df["Unit Price Numeric"] = df["Unit Price"].apply(to_float)
```

### Do any columns in the data set make the most sense to be encoded into labels for better statistical analysis?

Categorical columns can be encoded into labels for better statistical analysis and model building.

For example, the *Acquisition Method* is a nominal data with the following unique values

```python
df["Acquisition Method"].unique()

# Output
array(['WSCA/Coop', 'Informal Competitive', 'Statewide Contract',
       'Services are specifically exempt by statute', 'SB/DVBE Option',
       'NCB', 'Formal Competitive', 'Fair and Reasonable',
       'State Programs', 'Services are specifically exempt by policy',
       'CMAS', 'LCB', 'Master Purchase/Price Agreement',
       'Master Service Agreement', 'Emergency Purchase', 'CRP',
       'Software License Program', 'Special Category Request (SCR)',
       'Statement of Qualifications', 'State Price Schedule'],
      dtype=object)
```

To motivate the need for label encoding this column, let us create a simple bar plot of aggregate *Total Spend* per *Acuisition Method*

```python
spend_by_aq_method = df.groupby("Acquisition Method", as_index=False)\
                       .agg(number_of_purchases=("Total Price Numeric", "count"), \
                         total_spend=("Total Price Numeric", "sum"))\
                       .sort_values("total_spend", ascending=False)
```
```python
spend_by_aq_method.plot.bar(x="Acquisition Method", y="total_spend")
```

<center><img src="img/spend-by-aq-method.png" align="middle" style="width: 60%; height: 400px" /></center><br>

The above plot shows most of the purchases are made using one of the *Informal Competitive*, *Services are specifically exempt by statute*, *Formal Competitive*, or *Services are specifically exempt by policy* acquisition methods.

However, the plot looks busy and is hard to read. Label encoding the acquisition method makes it cleaner. Moreover, we may need to dummy-encode categorical columns like this in order to use them as features in model building.

Other columns that may benefit from label encoding:
- Acquisition Type
- Sub-Acquisition Type
- Sub-Acquisition Method

### Are there any obvious outliers or invalid/empty values in the labeled data set?

Most of the columns have missing values. Most notably, the *Requisition Number* and *Sub-Acquisition Method* columns have 331649 (95.8% of the rows) and 315122 (91% of the rows) missing values, respectively.

If we label-encode the *Sub-Acquisition Method* Column, there will be 315122 invalid codes (with value *-1*) representing the NULL values in that column. The following code snippet illustrates this.

```python
sub_aq_cat = df["Sub-Acquisition Method"].astype("category")
sub_aq_cat.cat.codes.value_counts()

# Output
-1     315122
 3      14148
 10     11602
 8       1810
 7        812
 4        565
 12       521
 9        503
 2        334
 0        328
 1        117
 11        83
 13        28
 5         18
 6         15
 15        10
 14         2
```

### What are the most expensive parts? What is the price distribution?
> **Assumption**: I assumed that "parts" in this question refers to the item being purchased described by the *Item Name* column.

The top ten most expensive items are

```python
df.loc[df["Unit Price"].notna(), ["Item Name", "Unit Price Numeric"]]\
  .sort_values("Unit Price Numeric", ascending=False).head(10)

# Output
        Item Name	        Unit Price Numeric
8790	Personal Service    $7,337,038,064.0
304848	04-36069 A10        $3,194,190,000.0
292165	Direct Service	    $3,010,052,803.0
314966	03-76182 A15	    $2,474,118,000.0
280645	03-76182 A18	    $2,253,227,000.0
48484	11-10019 A02	    $2,200,000,000.0
242591	Direct Service	    $1,979,109,000.0
339157	12-89334            $1,949,122,000.0
38396	04-35401 A14	    $1,948,168,000.0
212412	04-36069 A09	    $1,877,260,000.0
```
<!---
<center><img src="img/top-10-expensive.png" align="middle" style="width: 200px; height: 200px" /></center><br>
--->

Most of these purchases originated from the Department of Health Care Services, 
and the alpha-numeric values in the *Item Name* column seem to be (by Googling them) contract numbers under which the purchase is done.

Two things become obvious from the following price distribution

```python
print(df["Unit Price Numeric"].describe())
print("")
print(df["Total Price Numeric"].describe())

# Output
count    3.459880e+05
mean     4.326651e+05
std      2.136461e+07
min     -3.086123e+07
25%      3.468000e+01
50%      5.506650e+02
75%      1.019935e+04
max      7.337038e+09
Name: Unit Price Numeric, dtype: float64

count    3.459880e+05
mean     4.371353e+05
std      2.136468e+07
min     -3.086123e+07
25%      3.000000e+02
50%      3.600000e+03
75%      1.481420e+04
max      7.337038e+09
Name: Total Price Numeric, dtype: float64
```
<!---
<center><img src="img/describe-price.png" align="middle" style="width: 300px; height: 300px" /></center><br>
--->
1. There are some *invalid* values in the *Unit Price Numeric* & *Total Price Numeric* columns since prices cannot be negative.

```python
df.loc[df["Total Price Numeric"] < 0].shape

(1438, 35)
```

2. It is also easy to see that few purchases of large dollar amount skew the distribution to the right. The following cell illustrate this point

```python
IQR = df["Total Price Numeric"].quantile(0.75) - df["Total Price Numeric"].quantile(0.25) 
df[df["Total Price Numeric"] > 3*IQR].shape

(45294, 35)
```

The distribution is heavily right-skewed and difficult to illustrate using histograms or box plots. 

If we cut-off the maximum price at $100,000 (~92 percentile), prices will have the following distribution

```python
expensive_items = df["Total Price Numeric"] > 1e5 # Roughly 92 percentile
invalid_item_price = df["Total Price Numeric"] < 0
total_price_hist = df.loc[(~expensive_items) & (~invalid_item_price), "Total Price Numeric"].plot(kind="hist", bins=20, ec='black')
total_price_hist.set_xlabel("Total Price ($)")
```

<center><img src="img/price-hist.png" align="middle" style="width: 300px; height: 200px" /></center><br>

About half of the purchases are cheaper than $5000 dollars, and the total prices of about 90\% of the purchases are less than $100,000.

However, we cannot simply discard the few high-dollar purchases as outliers due to their high business value. The following code snippet illustrates this point. The top 1% purchase orders constitute about 92% of the total purchase order spend.

```python
q99 = df["Total Price Numeric"].quantile(0.99)
valid_price = df["Total Price Numeric"] >= 0

top1_pct = df.loc[df["Total Price Numeric"] > q99, "Total Price Numeric"].sum()
total = df.loc[valid_price,"Total Price Numeric"].sum()

print(f"${top1_pct:,.0f}")
print(f"{100*top1_pct / total:.1f}%")

# Output
$139,002,878,107
91.8%
```

### How has Purchase Order spend been trending over time?

>**Assumptions**: One critical assumption in this section is that the Creation Date is being used as a proxy for the actual Purchase Date because the Purchase Date column contains many null/invalid values. However, we should keep in mind that purchase order records are sometimes created on a later date than the actual purchase date.

The following code snippet shows the spend trend over the years 2012 - 2015
```python
df["Creation Year"] = pd.to_datetime(df["Creation Date"]).dt.to_period('Y')
valid_price = df["Total Price Numeric"] >= 0

spend_trend = df[valid_price].groupby("Creation Year", as_index=False).agg(Spend=("Total Price Numeric", "sum"))
```
<center><img src="img/spend-by-year.png" align="middle" style="width: 300px; height: 200px" /></center><br>

In general, the spending trend over the years has been growing. The spike in 2013 is the result of a few high-dollar spends whose actual purchase date backdates the creation date.

Similarly, the purchase trend can be shown at a month-level, for example to check for seasonality.

### Which departments are spending the most money?

The top 10 departments by spend are:
```python
spend_per_dept = df.groupby("Department Name", as_index=False).agg(num_of_purchases=("Total Price Numeric","count"), total_spend=("Total Price Numeric","sum")).sort_values("total_spend", ascending=False)
spend_per_dept["pct_of_total"] = spend_per_dept["total_spend"].apply(lambda x: round(100 *(x/spend_per_dept["total_spend"].sum()),2))
spend_per_dept.head(10)

# Output
    Department Name                                 num_of_purchases    total_spend	pct_of_total
56  Health Care Services, Department of             2862                $99,759,350,736	65.96
81  Public Health, Department of                    4091                $5,621,707,894	3.72
92  Social Services, Department of                  2323                $5,565,328,198	3.68
31  Corrections and Rehabilitation, Department of   57537               $4,711,857,451	3.12
93  State Hospitals, Department of                  18968               $4,545,650,046	3.01
105 Transportation, Department of                   17644               $4,347,882,800	2.87
57  High Speed Rail Authority, California           489                 $3,565,361,682	2.36
110 Water Resources, Department of                  28331               $2,790,266,201	1.84
30  Correctional Health Care Services               32220               $2,641,173,668	1.75
38  Employment Development Department	            3412                $1,724,960,851	1.14
```
<!--- 
<center><img src="img/spend-by-dept.png" align="middle" style="width: 400px; height: 200px" /></center><br>
--->

About 66% of the spending comes from the Department of Health Care Services, which has spent close to 100 billion dollars over 2862 purchase orders.
Departments of Public Health and Social Services are distant second and third, 
each of them spending about 3.7% of the total.

### Which zip code has the most supplier concentration? Any idea why?

Zip Code 95691 has the most supplier concentration with  11095 (around 4%) of the purchases originating from that zip code.

```python
df["Supplier Zip Code"].value_counts()

# Output
95691         11095
95814         10921
95696          8518
95827          7159
95841          7008
              ...  
53141-1410        1
11201             1
2134              1
91386             1
55044             1
```

Let us check the suppliers located in zip code 95691 and the number of purchases completed from them

```python
df.loc[df["Supplier Zip Code"] == '95691', "Supplier Name"].value_counts()

# Output
Grainger Industrial Supply                   9441
MMG Technology Group Inc                      310
Paper Distributors Inc                        219
NOR CAL PERFORMANCE                           135
ANCHOR SUPPLY                                 105
                                             ... 
AFM ENVIRONMENTAL, INC                          1
Michael Palmer                                  1
Kutsch, Inc. dba: B&R Head & Block Repair       1
KEVCO, INC.                                     1
Graebel                                         1
Name: Supplier Name, Length: 93, dtype: int64
```

Out of 11095 purchases made from suppliers in zip code 95691, 9441 (about 85%) of the purchases are made from *Grainger Industrial Supply*

Let's go a bit deeper and see the Acquisition Methods used to purchase from Grainger Industrial Supply

```python
df.loc[df["Supplier Name"] == "Grainger Industrial Supply", "Acquisition Method"].value_counts()

# Output
WSCA/Coop                                     9267
Informal Competitive                           105
Fair and Reasonable                             62
SB/DVBE Option                                   2
Formal Competitive                               2
State Programs                                   1
Services are specifically exempt by policy       1
NCB                                              1
Name: Acquisition Method, dtype: int64
```

9267 (more than 98%) of the purchases made from *Grainger Industrial Supply* are of type *WSCA/Coop* Acquisition Method.

### What are the top UNSPSC categories? 

>**Assumptions**: 
>1. I assume that "UNSPSC categories" corresponds to the "Family Title" column 
>2. Since it is not explicitly mentioned, I assumed that "top" refers to the highest number of purchases instead of total amount.

With these assumption, the top 10 UNSPSC categories by number of purchases are
```python
top_unspsc = df.groupby("Family Title", as_index=False)\
    .agg(count=("Family Title", "count"), total_spend=("Total Price Numeric", "sum"))\
    .sort_values(["count", "total_spend"], ascending=False)
top_unspsc.head(10)

# Output
	Family Title	                                    count	total_spend
265	Office machines and their supplies and accesso...   16479	$88,940,549
150	Fuels                                               14599	$288,534,768
59	Computer services                                   13946	$1,547,035,757
58	Computer Equipment and Accessories                  13851	$273,810,522
285	Paper products	                                    10772	$117,600,163
394	Vocational training                                 9785	$1,859,963,869
266	Office supplies	                                    9342	$31,120,654
358	Software                                            8274	$1,255,535,652
335	Refuse disposal and treatment	                    5433	$155,610,528
0	Accommodation furniture	                            5177	$80,508,132
```

### If you could spend another day cleaning up the data to make it more useful what might you do?

- Columns like the *Classification Code* and *Location* include the new line character ("\n") to separate a list of values. If those columns are to be analyzed, we need to remove the new line character and extract the actual values

### If you could find another data set that would complement this one to help answer the above or similar questions, what dataset might be ideal?

### Future work

- To better understand the price distribution, a variety of probability density functions (PDF) can be fitted to the price column to select the best fit

- The trend of purchase order spend is discussed above at a year granularity level. A similar analysis can be done at month-level, e.g., to check for seasonality