from dagster import In, OpExecutionContext, Out, op
import pandas as pd
import operator


@op(name="mock_csv_data", out=Out())
def mock_csv_data(context: OpExecutionContext) -> pd.DataFrame:
    data = [["column1", "column2", "column3"], [1, 2, 3], [4, 5, 6], [7, 8, 9]]
    context.log.info(f"Mock data: {data}")

    df = pd.DataFrame(data[1:], columns=data[0])
    context.log.info(f"DataFrame created from mock data:\n{df}")

    return df


@op(name="write_csv", ins={"result": In(pd.DataFrame)}, out=Out(str))
def write_csv(context: OpExecutionContext, result: pd.DataFrame) -> str:
    context.log.info(f"Received data to write to CSV:\n{result}")

    result.to_csv("output.csv", index=False)

    context.log.info(f"Data written to output.csv")
    return "output.csv"


@op(
    name="math_block",
    ins={
        "data": In(pd.DataFrame),
        "operand": In(str),
        "constant": In(float),
    },
    out=Out(pd.DataFrame),
)
def math_block(
    context: OpExecutionContext,
    operand: str,
    constant: float,
    data: pd.DataFrame,
) -> pd.DataFrame:
    operand = getattr(operator, operand)
    context.log.info(f"Applying math operation: {operand.__name__}")
    result = data.apply(lambda x: operand(x, constant), axis=1)
    context.log.info(f"Data after {operand.__name__} operation:\n{result}")
    return result
