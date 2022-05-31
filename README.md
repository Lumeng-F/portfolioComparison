# Compare Portfolio

README

  A tool to help visualize how your portfolio would look like if you only buy a certain stock. 
  
  Since most sites/app I found doesn't consider the contribution and withdrawls, I had to make one.
  
  The project is still very sloppy, eg. it can't actually take user uploads, the code is messy.
  
  Things I plan to add: ability to add mutiple tickers as a real portfolio, account for dividends withour user manully change the price.

INSTRUCTION

  Shares bought with dividend should have a price of 0. (Since your compared ticker may not pay the dividend, therefore you cannot buy the shares)
  
  File should be in .csv.
  
  File should be formated as 
  
      Date       | Ticker | Price | Amount
      2022-08-03 | ZIM    | 70.07 | 20
      
  Since I don't know how to do things, after uploading your file, save and re-run the routes.py. Your portfolio should appear.
 
  If you don't need all these, open just_line.py, put file path and tickers you wish to compare, then run.
  
 DEPENDENCIES
 
  Pands/ Flask/ Plotly/ yfinance 
  
