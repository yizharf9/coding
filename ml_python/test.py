import pandas as pd

countries_pd = [
    {
        "name":"israel",
        "birth":67,
    },
    {
        "name":"usa",
        "birth":81,
    },
    {
        "name":"greece",
        "birth":42,
    },
]


countries_pd = pd.DataFrame(countries_pd)
print(countries_pd.sort_values())

