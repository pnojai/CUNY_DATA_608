library(ggplot2)
library(dplyr)
library(stringr)

df <- read.csv("mortality.csv") #, stringsAsFactors = F)
# names(df)
names(df) <- str_replace_all(string = names(df), pattern = "\\.", replacement = "_")
# names(df)
# head(df)

df_2010 <- df %>%
    filter(Year == 2010)
cod_labels <- unique(as.character(df_2010$ICD_Chapter))
str_trunc(cod_labels, 40)

summary(df_2010$Crude_Rate)
df_2010 %>%
    arrange(desc(Crude_Rate))

df_slice <- df_2010 %>%
    filter(ICD_Chapter == "Neoplasms")

ggplot(df_slice) +
    aes(reorder(State, Crude_Rate), Crude_Rate) +
    geom_bar(stat = "identity") +
    coord_flip() +
    theme_bw() +
    labs(title = "Crude Mortality Rate in the U.S. in 2010 by State",
         subtitle = "Cause of death: Neoplasms",
         x = "State",
         y = "Crude Mortality Rate (per 100,000)",
         caption = "Source: CDC")

unique(df$Year)

df %>%
    arrange(Year, State)

# U.S. population by year.
df_pop <- df %>%
    filter(ICD_Chapter == "Neoplasms") %>%
    group_by(Year) %>%
    summarise(pop_tot = sum(Population))

# State population weight.
df_pop_wt <- df %>%
    inner_join(df_pop) %>%
    select(ICD_Chapter, State, Year, Population, pop_tot) %>%
    arrange(State, Year) %>%
    mutate(pop_wt = Population / pop_tot)

# Join mortality and population weight.
df_join_wt <- df %>%
    inner_join(df_pop_wt)

# Sanity check. Weights should sum to 1 for a given year and cause of death.
# And they do.
df_join_wt %>%
    filter(Year == 1999, ICD_Chapter == "Neoplasms") %>%
    summarise(sum(pop_wt))

# Add weighted mortality to dataframe
df_join_wt <- df_join_wt %>%
    mutate(mort_weighted = Crude_Rate * pop_wt)

# Plot trend of national average mortality rate for a given cause of death.
df_join_wt %>%
    filter(ICD_Chapter == "Neoplasms") %>%
    group_by(Year) %>%
    summarize(natl_mort = sum(mort_weighted)) %>% # National avg weighted by pop.
    ggplot(aes(x = Year, y = natl_mort)) +
    geom_line()

# Plot a state's mortality rate.
df_join_wt %>%
    filter(ICD_Chapter == "Neoplasms", State == "OH") %>%
    ggplot(aes(x = Year, Crude_Rate)) + # State reports crude rate.
    geom_line()

# THIS IS NOT THE REQUIREMENT. All states, separately.
df_join_wt %>%
    filter(ICD_Chapter == "Neoplasms") %>%
    group_by(State, Year) %>%
    ggplot() +
    geom_line(aes(x = Year, y = Crude_Rate)) +
    facet_wrap(~State, ncol = 5)

# Dataframe for national mortality.
df_natl_mort <- df_join_wt %>%
    filter(ICD_Chapter == "Neoplasms") %>%
    group_by(Year) %>%
    summarize(natl_mort = sum(mort_weighted)) 

# Dataframe for one state.
df_state_mort <- df_join_wt %>%
    filter(ICD_Chapter == "Neoplasms", State == "NY") 

ggplot() + 
    geom_line(data = df_natl_mort, aes(x = Year, y = natl_mort), color = "black") +
    geom_line(data = df_state_mort, aes(x = Year, y = Crude_Rate), color = "red")

########################################################################
#                           PLOTLY
########################################################################

# https://www.musgraveanalytics.com/blog/2018/7/24/how-to-order-a-plotly-bar-chart-in-r

library(plotly)

fig <- plot_ly(data = df_slice, x = ~Crude_Rate, y = ~State,
               type = "bar", orientation = "h") %>%
    layout(
        title = "",
        xaxis = list(title = "Crude Mortality Rate (per 100,000)"),
        yaxis = list(title = "State",
                     categoryorder = "total ascending")
    )

fig.show