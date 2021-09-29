# -*- coding: utf-8 -*-
# Implemented By: Hoai Nam
import xlrd
import csv

class Excel():
    def __init__(self, excelfilepath, sheetname):
        self._book = xlrd.open_workbook(excelfilepath, on_demand = True) 
        
        if str(sheetname).isdigit():
            self._worksheet = self._book.sheet_by_index(sheetname)            
        else:
            self._worksheet = self._book.sheet_by_name(sheetname)

    def GetCellValue(self, row, col):
        result = self._worksheet.cell_value(rowx=row, colx=col)                
        return result
    
    def GetHeaderColumnName(self):
        headerlist = [self._worksheet.cell_value(0, i) for i in xrange(self._worksheet.ncols)]
        return headerlist

    def GetHeaderColumnIndex(self, headercolname):
        index = -1
        headerlist = self.GetHeaderColumnName()
        if headercolname in headerlist:
            index = headerlist.index(headercolname)
        return index

    def GetCellValueByColumnName(self, row, colheadername):
        cellvalue = ""
        colheaderindex = self.GetHeaderColumnIndex(colheadername)
        if colheaderindex >= 0:
            cellvalue = self.GetCellValue(row, colheaderindex)
        return cellvalue
    
    def GetColumnValues(self, headercolname):
        columnvalues = []
        indx = self.GetHeaderColumnIndex(headercolname)
        columnvalues = [self._worksheet.cell_value(i, indx) for i in xrange(1, self._worksheet.nrows)]
        return columnvalues

    def GetRowValues(self, row):
        rowvalues = []
        rowvalues = [self._worksheet.cell_value(row, i) for i in xrange(self._worksheet.ncols)]
        return rowvalues

    def GetCellIndexByValue(self, value, operator="in"):
        cellindex = []
        for x in xrange(self._worksheet.nrows):
            rowvalues = self.GetRowValues(x)            
            rowvalues = [str(u) for u in rowvalues]
            
            tmp_flag = []
            if operator == "in":
                tmp_flag = [t for t in rowvalues if value in t]
            elif operator == "=":
                tmp_flag = [t for t in rowvalues if value == t]
            
            if len(tmp_flag) > 0:
                col = rowvalues.index("".join(tmp_flag))
                cellindex = [x,col]
                break
        return cellindex

    def GetTotalRows(self):
        totalrows = 0
        totalrows = self._worksheet.nrows
        return totalrows

    def GetTotalCols(self):
        totalcols = 0
        totalcols = self._worksheet.ncols
        return totalcols

    def GetRowIndexByValue(self, columnname, searchvalue):
        # This action is used to get row index of given column based on search value
        row = -1
        colindx = self.GetHeaderColumnIndex(columnname)
        for i in xrange(1, self._worksheet.nrows):
            cellvalue = self.GetCellValue(i, colindx)
            if searchvalue in cellvalue:
                row = i
                break
        return row

    def GetRowIndexesByFilter(self, columnname, filtervalue, operater="="):
        # this action is used to get list row index based on filter column value
        rows = []        
        colindx = self.GetHeaderColumnIndex(columnname)
        for i in xrange(1, self._worksheet.nrows):
            cellvalue = self.GetCellValue(i, colindx)
            expr = False
            if operater == "=":
                expr = filtervalue == cellvalue
            elif operater == "in":
                expr = filtervalue in cellvalue
            else:
                expr = False

            if expr:
                tmp = rows.append(i)
        return rows

    def GetColValuesByColFilter(self, destinationcolumnname, filtercolumn, filtercolumnvalue, operater="="):
        # This action is used to get all values on one column based on filter of another column
        columnvalues = []

        # get row index of filter column containing filter value
        rows = self.GetRowIndexesByFilter(filtercolumn, filtercolumnvalue, operater)

        if len(rows) > 0:

            # get index of destination column
            descol = self.GetHeaderColumnIndex(destinationcolumnname)
            for row in rows:
                # get value based on col index and row index
                value = self.GetCellValue(row, descol)
                tmpvalues = columnvalues.append(value)
        return columnvalues

    def GetColValuesByFilterCols(self, destinationcolumnname, filtercolsdict, operater="="):
        # This action is used to get all values on one column based on filter of another column
        columnvalues = []

        # get row index of filter column containing filter value
        listrows = []
        if len(filtercolsdict) > 0:
            for filtercolumn in filtercolsdict:
                filtercolvalue = filtercolsdict[filtercolumn]
                currentrows = []
                
                # [Nam Nguyen, 19-Dec-2018]: Modified script to search empty value
                # Including search empty value, not handle search empty or None value
                currentrows = self.GetRowIndexesByFilter(filtercolumn, filtercolvalue, operater)
                
                # append to list
                tmp = listrows.append(currentrows)

        # if there are null list in, because of some value are wrong, will skip this filter
        if (len(listrows) > 0) and ([] not in listrows):

            # get common rows in list
            rows = list(reduce(lambda x, y: x & y, (set(i) for i in listrows)))

            # sort list
            tmp = rows.sort()

            # get index of destination column
            descol = self.GetHeaderColumnIndex(destinationcolumnname)
            for row in rows:
                # get value based on col index and row index
                value = self.GetCellValue(row, descol)
                tmpvalues = columnvalues.append(value)
        return columnvalues

class CSV():
    def __init__(self, csvfilepath, delimiter):
        self._f = open(csvfilepath, 'rb')
        self._content = csv.reader(self._f, delimiter = delimiter)
        self._lstcontent = list(self._content)
        # [20-Feb-2019, Nam]: Add step to close csv file to avoid error "Too many open file".
        self._f.close()        

    def GetTotalRows(self):
        return len(self._lstcontent)
    
    def GetHeaderColumnName(self):
        return self._lstcontent[0]

    def GetHeaderColumnIndex(self, columnname):
        try:
            headercolname = self.GetHeaderColumnName()
            index = headercolname.index(columnname)
        except:
            index = -1
        return index

    def GetCellValue(self, row, col):
        cellvalue = ""
        try:
            cellvalue = self._lstcontent[row][col]
        except:
            cellvalue = ""
        return cellvalue

    def GetCellValueByColumnName(self, row, colname):
        cellvalue = ""
        try:
            col = self.GetHeaderColumnIndex(colname)
            cellvalue = self._lstcontent[row][col]
        except:
            cellvalue = ""
        return cellvalue

    def GetColumnValues(self, colname):
        colvalues = []
        try:
            col = self.GetHeaderColumnIndex(colname)
            for rowvalue in self._lstcontent:
                cellvalue = rowvalue[col]
                tmp = colvalues.append(cellvalue)
            # remove first data as header column name
            tmp = colvalues.remove(colname)
        except:
            colvalues = []
        return colvalues
    
    def GetRowIndexesByFilter(self, columnname, filtervalue, operater="="):
        # this action is used to get list row index based on filter column value
        rows = []
        colindx = self.GetHeaderColumnIndex(columnname)
        for i in xrange(1, len(self._lstcontent)):
            cellvalue = self.GetCellValue(i, colindx)
            expr = False
            if operater == "=":
                expr = filtervalue == cellvalue
            elif operater == "in":
                expr = filtervalue in cellvalue
            else:
                expr = False

            if expr:
                tmp = rows.append(i)
        return rows

    def GetColValuesByFilterCols(self, destinationcolumnname, filtercolsdict, operater="="):        
        # This action is used to get all values on one column based on filter of another column
        columnvalues = []

        # get row index of filter column containing filter value
        listrows = []
        if len(filtercolsdict) > 0:            
            for filtercolumn in filtercolsdict:
                filtercolvalue = filtercolsdict[filtercolumn]                
                currentrows = []
                if filtercolvalue != None and filtercolvalue != "":                
                    currentrows = self.GetRowIndexesByFilter(filtercolumn, filtercolvalue, operater)
            
                # append to list
                tmp = listrows.append(currentrows)

        # if there are null list in, because of some value are wrong, will skip this filter
        if (len(listrows) > 0) and ([] not in listrows):

            # get common rows in list
            rows = list(reduce(lambda x, y: x & y, (set(i) for i in listrows)))

            # sort list
            tmp = rows.sort()

            # get index of destination column
            descol = self.GetHeaderColumnIndex(destinationcolumnname)
            for row in rows:
                # get value based on col index and row index
                value = self.GetCellValue(row, descol)
                tmpvalues = columnvalues.append(value)
        return columnvalues
