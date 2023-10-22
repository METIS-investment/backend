import math, json, requests


def logistic(x, a, k):
    return 1 / (1 + math.exp(-k * (x - a)))


def get_world_bank_data(indicator, country_code):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json"
    response = requests.get(url)
    data = json.loads(response.text)
    latest_value = None
    for entry in data[1]:
        if entry["value"] is not None:
            latest_value = entry["value"]
            break
    return latest_value


def investment_worthyness(country_code, founded_year, profit_pa, revenue_pa, book_value):
    weight_stability = 3
    weight_year = 2
    weight_gdp = 2
    weight_profit_margin = 5
    weight_book_value = 1

    total = weight_stability + weight_year + weight_gdp + weight_profit_margin + weight_book_value

    return (weight_stability * stability_country(country_code) + weight_year * year(
        founded_year) + weight_gdp * gdp_growth_rate(country_code) + weight_profit_margin * profit_margin(profit_pa,
                                                                                                          revenue_pa) + weight_book_value * book_value) / total * 100


def year(founded_year):
    return logistic((2023 - founded_year), 3.2, 1.2)


def stability_country(country_code):
    # Indicator code for intentional homicides (per 100,000 people)
    violence_indicator = "VC.IHR.PSRC.P5"

    violence_rate = get_world_bank_data(violence_indicator, country_code)

    return logistic(violence_rate, -0.2, 2.1)


def gdp_growth_rate(country_code):
    # Indicator code for GDP growth rate
    gdp_growth_indicator = "NY.GDP.MKTP.KD.ZG"

    gdp_growth_rate = get_world_bank_data(gdp_growth_indicator, country_code)

    return logistic((gdp_growth_rate), 5.3, 0.4)


def profit_margin(profit_pa, revenue_pa):
    return (profit_pa / revenue_pa)


if __name__ == "__main__":
    country_code = "US"  # Example country code for the United States
    founded_year = 2018  # Example founded year
    profit_pa = 1000000  # Example profit per annum
    revenue_pa = 10000000  # Example revenue per annum
    book_value = 0  # Example value = assets - liabilities

    invest_worthyness = investment_worthyness(country_code, founded_year, profit_pa, revenue_pa, book_value)

    print("Investment worthyness in percent: " + "{:.2f}".format(invest_worthyness) + "%")


x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
y_data = [10, 45, 200, 700, 700, -500, -200, -200, -750]
cfactor = 0.5
bookvalue = 0

# Define the polynomial model function (you can adjust the degree of the polynomial)
def polynomial_model(x, *coefficients):
    return np.polyval(coefficients, x)


# Function to perform polynomial regression on a set of points
def perform_polynomial_regression(x_data, y_data, degree=2):
    # Fit a polynomial curve to the data
    coefficients = np.polyfit(x_data, y_data, degree)

    # Define the fitted polynomial model function
    def fitted_polynomial(x):
        return polynomial_model(x, *coefficients)

    return fitted_polynomial, coefficients


# Example data points

# Perform polynomial regression and get the fitted function
fitted_function, coefficients = perform_polynomial_regression(x_data, y_data, degree=2)

# Use the fitted function to make predictions
x_value = 6
max = 1
predicted_y = fitted_function(x_value)
compvalue = 0
for i in range(max, max + 36, 1):
    compvalue += fitted_function(i)
compvalue *= cfactor
compvalue += bookvalue
if (compvalue < 1000):
    compvalue = 1100/(1+(np.exp(-0.0015*compvalue)))
print(compvalue)