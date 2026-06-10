import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd


def run_job(input_directory, output_directory):

    # Carga de la tabla drivers
    drivers = pd.read_csv(
        f"{input_directory}/drivers.csv",
        sep=",",
        thousands=None,
        decimal=".",
    )

    # Carga de la tabla timesheet
    timesheet = pd.read_csv(
        f"{input_directory}/timesheet.csv",
        sep=",",
        thousands=None,
        decimal=".",
    )

    # Media de la cantidad de horas y millas de cada conductor por año
    mean_timesheet = timesheet.groupby("driverId").mean(numeric_only=True)

    # Eliminación de la columna 'week'
    mean_timesheet = mean_timesheet.drop(columns=["week"])

    # Registros con valores por debajo de la media del grupo
    mean_hours_logged_by_driver = timesheet.groupby("driverId")["hours-logged"].transform("mean")

    timesheet_with_means = timesheet.copy()
    timesheet_with_means["mean_hours-logged"] = mean_hours_logged_by_driver

    timesheet_below = timesheet_with_means[
        timesheet_with_means["hours-logged"] < timesheet_with_means["mean_hours-logged"]
    ]

    # Cómputo de la cantidad de horas y millas de cada conductor por año
    sum_timesheet = timesheet.groupby("driverId").sum(numeric_only=True)
    sum_timesheet = sum_timesheet[["hours-logged", "miles-logged"]].reset_index()

    # Unión de las tablas
    summary = pd.merge(
        sum_timesheet,
        drivers[["driverId", "name"]],
        on="driverId",
    )

    # Almacenamiento de los resultados
    os.makedirs(output_directory, exist_ok=True)
    summary.to_csv(
        f"{output_directory}/summary.csv",
        sep=",",
        header=True,
        index=False,
    )

    # Ordenamiento por la cantidad de millas registradas
    top10 = summary.sort_values(by="miles-logged", ascending=False).head(10)
    top10 = top10.set_index("name")

    # Gráfico de barras horizontales
    top10["miles-logged"].plot.barh(color="tab:orange", alpha=0.6)
    plt.gca().invert_yaxis()
    plt.gca().get_xaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
    )
    plt.xticks(rotation=90)
    plt.gca().spines["left"].set_color("lightgray")
    plt.gca().spines["bottom"].set_color("gray")
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    plots_directory = output_directory.replace("output", "plots")
    os.makedirs(plots_directory, exist_ok=True)
    plt.savefig(f"{plots_directory}/top10_drivers.png", bbox_inches="tight")
    plt.close()


run_job(
    "files/input",
    "files/output",
)