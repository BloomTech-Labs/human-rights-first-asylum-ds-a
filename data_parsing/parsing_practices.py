# Data Parsing - Best Practices
# 1.  All parsers are not tied to individual formats - the data format for the input and output of the parser is up to each individual parser. 
# 2. The larger the amount of data that is being parsed, the more sophisticated the parser must be - because it will be reading more language/terms and will generally have more to look for. This also means that as the parser gets more sophisticated, maintaining this tool will be necessary
# 3. When building the parser, parse one attribute at a time so you know that the information is coming out in the correct format
# 4. The simpler the better. Rather than using a complex regex, there are various matchers that can simplify the code. This makes it easier to understand what the parser is looking for in the search and makes it easier to edit in the future. 
# 
#
# Possible Parsing Libraries to Use - 
# 1. PFNET is originally a C library that has a completed python branch. - It uses Cython so you know it's fast
# 2. PDFMiner - 2nd choice
# 3. py-pdf-parser

