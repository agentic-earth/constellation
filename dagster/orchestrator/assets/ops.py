import operator
from dagster import OpExecutionContext, asset, op
import pandas as pd


@asset
def mock_csv_data(ctx: OpExecutionContext) -> pd.DataFrame:
    data = [["column1", "column2", "column3"], [1, 2, 3], [4, 5, 6], [7, 8, 9]]
    ctx.log.info(f"Mock data: {data}")

    df = pd.DataFrame(data[1:], columns=data[0])
    ctx.log.info(f"DataFrame created from mock data:\n{df}")

    return df


@asset
def write_csv(ctx: OpExecutionContext, result: pd.DataFrame) -> str:
    ctx.log.info(f"Received data to write to CSV:\n{result}")

    result.to_csv("output.csv", index=False)

    ctx.log.info(f"Data written to output.csv")
    return "output.csv"


@op
def math_block(
    ctx: OpExecutionContext,
    operand: str,
    constant: float,
    data: pd.DataFrame,
) -> pd.DataFrame:
    operand = getattr(operator, operand)
    ctx.log.info(f"Applying math operation: {operand.__name__}")
    result = data.apply(lambda x: operand(x, constant), axis=1)
    ctx.log.info(f"Data after {operand.__name__} operation:\n{result}")
    return result
