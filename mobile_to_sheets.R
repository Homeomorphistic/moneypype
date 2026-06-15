# mobile_to_sheets.R
# Transform xlsx from mobile app into .csv readable in Google Sheets.

prepare_category_map <- function(file="categories_map.csv") {
  #' Prepare a mapping between categories and types.
  #'
  #' It's done by creating named vector, with names as categories,
  #' and values as corresponding types.
  #'
  #' @param file character. A filename for table with mapping.
  #'    Table should contain columns "Category" and "Type".
  #' @return map_to_type function. A function of categories,
  #'    returning type.

  category_table <- read.csv(file)
  map <- category_table$Type
  names(map) <- category_table$Category

  map_to_type <- function(category) {
    #' Map a category to the type
    #'
    #' @param category character. A string with category names.
    #' @return character. A string with corresponding type names.

    return(map[category])
  }

  return(map_to_type)
}

transform_transfers <- function(transfers) {
  #' Transform transfers table to match the accounting format.
  #'
  #' Transfers table coming from mobile app has a format:
  #' amount | account_1 | account_2,
  #' but we need:
  #' account_1 | -amount
  #' account_2 | +amount
  #'
  #' @param transfers data.frame. A data.frame with transfers data from mobile app.
  #' @return data.frame. A data.frame with transformed transfers data.

  from <- data.frame(date=transfers$`Data i godzina`, account=transfers$`Wychodzące`,
                     category="Transfer", type="Transfer", note=transfers$Komentarz,
                     currency=transfers$`Waluta wychodząca`,
                     amount= - transfers$`Kwota w walucie wychodzącej`,
                     ref_currency_amount= - transfers$`Kwota w walucie wychodzącej`,
                     label=NA)
  to <- data.frame(date=transfers$`Data i godzina`, account=transfers$`Przychodzące`,
                   category="Transfer", type="Transfer", note=transfers$Komentarz,
                   currency=transfers$`Waluta wychodząca`,
                   amount=transfers$`Kwota w walucie wychodzącej`,
                   ref_currency_amount=transfers$`Waluta w kwocie przychodzącej`,
                   label=NA)

  return(rbind(from, to))
}

transform_income_expense <- function(df, map, default_other) {
  #' Transform income or expanses table to match budgeting format.
  #'
  #' @param df data.frame. A data.frame containing income or expenses data.
  #' @param map function. A function to map categories to types.
  #' @param default_other character. A default value for category "Other".
  #' @return data.frame. A data.frame containing income or expenses in
  #'    matching format.

  types <- map(df$Kategoria)
  # Fill missing values with default "other".
  types[is.na(types)] <- default_other

  # If the table is expense, then we need to add minus sign.
  if(default_other!="Income"){
    df$`Kwota w walucie domyślnej` <- - df$`Kwota w walucie domyślnej`
    df$`Kwota w walucie konta` <- - df$`Kwota w walucie konta`
  }

  # By default Other category is named Inne in our app.
  df[df$Kategoria == "Inne", "Kategoria"] <- "Other"

  budget <- data.frame(date=df$`Data i godzina`, account=df$Konto,
                       category=df$Kategoria, type=types, note=df$Komentarz,
                       currency=df$`Waluta konta`,
                       amount=df$`Kwota w walucie domyślnej`,
                       ref_currency_amount=df$`Kwota w walucie konta`,
                       label=df$Etykietki)
  return(budget)
}

convert_dates <- function(df) {
  #' Convert from polish dates to standard IT format.
  #'
  #' @param df data.frame. A data.frame contaning date column.
  #' @return df data.frame. A data.frae with converted dates.

  # Prepare polish to number date correspondance.
  polish_dates <- c("stycznia", "lutego", "marca", "kwietnia", "maja",
                    "czerwca", "lipca", "sierpnia", "września", "października",
                    "listopada", "grudnia")
  mo_num <- 1:12
  names(mo_num) <- polish_dates
  
  # Split strings and convert polish named months to standard form.
  dates <- strsplit(df$date, " ")
  dates <- sapply(dates, function (date) paste(date[3], mo_num[date[2]], date[1], sep = "-") )
  dates <- as.Date(dates, format = "%Y-%m-%d")

  df$date <- dates
  return(df)
}

convert_numbers_to_excel <- function(df) {
  #' Convert numbers (dot) to match excel format (comma).
  #'
  #' @param df data.frame. A data.frame contaning numeric columns.
  #' @return df data.frame. A data.frame with converted numeric columns.

  df$amount <- sub("\\.", ",", as.character(df$amount))
  df$ref_currency_amount <- sub("\\.", ",",
                                as.character(df$ref_currency_amount))
  return(df)
}

save_all <- function(income, expenses, transfers, filename="budget.csv") {
  #' Save income, expenses and transfers in one file.
  #'
  #' @param filename character. A string with filename.
  #' @param ... data.frame. A data.frames to save.
  #' @return data.frame. A data.frame containing all tables.

  df <- rbind(income, expenses, transfers)
  # Sort by date.
  df <- df[order(df$date), ]
  write.csv(df, paste(Sys.Date(), filename, sep = "_"), row.names = FALSE)

  return(df)
}

# Library for excel reading
library(readxl)

# Get filepath.
file_path <- "2026/2026_05_31_17_16_58_998344.xlsx"
# Read xlsx files.
income <- read_excel(file_path, sheet = "Dochody", skip = 1)
expenses <- read_excel(file_path, sheet = "Wydatki", skip = 1)
transfers <- read_excel(file_path, sheet = "Przelewy", skip = 1)

# Map between categories and types.
map <- prepare_category_map()

# Transform data to match budgeting format.
income <- transform_income_expense(income, map, "Income")
expenses <- transform_income_expense(expenses, map, "Wants")
transfers <- transform_transfers(transfers)

# income <- convert_dates(income) # the app changed date format.
# expenses <- convert_dates(expenses)
# transfers <- convert_dates(transfers)

income <- convert_numbers_to_excel(income)
expenses <- convert_numbers_to_excel(expenses)
transfers <- convert_numbers_to_excel(transfers)

# Save all tables.
test <- save_all(income, expenses, transfers)