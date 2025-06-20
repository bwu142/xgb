# Copyright (c) 2025 Ben Wu <benjamin.x.wu@gmail.com>
# Distributed under the BSD 3-Clause License

import pytest
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import tree_filtering
import filter
import purify

##### CONTOUR PLOT HELPER FUNCTIONS #####


def plot_linear_one_var(model, equation):
    """
    Makes scatterplot containing z vs. x1 and z vs. x2
    """
    # Generate x_i vectors
    x_step = np.arange(0, 100, 0.1)  # 0.1 step, not including 100
    x_random = np.random.uniform(0, 100, size=len(x_step))

    # Pandas Dataframes
    X_test1 = pd.DataFrame({"x1": x_step, "x2": x_random})
    X_test2 = pd.DataFrame({"x1": x_random, "x2": x_step})

    # Get predicted values
    y_pred_x1 = tree_filtering.predict(model, (0,), X_test1)
    y_pred_x2 = tree_filtering.predict(model, (1,), X_test2)

    # Plot
    plot = go.Figure()

    plot.add_trace(
        go.Scatter(
            x=X_test1["x1"],
            y=y_pred_x1,
            mode="lines",
            name="z_pred_x1",
            line=dict(color="red"),  # specify color here
        )
    )

    plot.add_trace(
        go.Scatter(
            x=X_test2["x2"],
            y=y_pred_x2,
            mode="lines",
            name="z_pred_x2",
            line=dict(color="blue"),  # different color here
        )
    )

    plot.update_layout(
        title=f"{equation}", xaxis_title="x1, x2", yaxis_title="Predicted z"
    )

    plot.show()


def plot_contour_one_var(model, equation, start_val, stop_val, step_val):
    """
    Generates two contour plots using predictions from f(x1), f(x2) respectively
    """
    # Generate all combinations of pairs (x1, x2) from 0 too 100 in .1 increments
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    # convert all pairs to DataFrame structure
    X_test = pd.DataFrame({"x1": all_pairs[:, 0], "x2": all_pairs[:, 1]})
    # get predictions
    z_pred_x1 = tree_filtering.predict(model, (0,), X_test)
    z_pred_x2 = tree_filtering.predict(model, (1,), X_test)

    # reshape Z3 vector into 2D numpy array for contour plotting (rows: x2, cols: x1)
    Z_Pred_x1 = z_pred_x1.reshape(len(x2), len(x1))
    Z_Pred_x2 = z_pred_x2.reshape(len(x2), len(x1))

    # Z_Pred_x1
    contour_plot_Z_Pred_x1 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x1,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=start_val,
                end=stop_val,
                size=step_val,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )

    contour_plot_Z_Pred_x1.update_layout(
        title=f"Z_Pred_x1: {equation}",
        xaxis_title="x1",
        yaxis_title="x2",
    )

    contour_plot_Z_Pred_x1.show()

    # Z_Pred_x1
    contour_plot_Z_Pred_x2 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x2,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=start_val,
                end=stop_val,
                size=step_val,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )

    contour_plot_Z_Pred_x2.update_layout(
        title=f"Z_Pred_x2: {equation}",
        xaxis_title="x1",
        yaxis_title="x2",
    )

    contour_plot_Z_Pred_x2.show()


def plot_contour_two_vars(model, equation, start_val, stop_val, step_val):
    """
    model: XGBRegressor
    equation: string

    Generates one contour plot using prediction from f(x1x2)


    """
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    # convert all pairs to DataFrame structure
    X_test = pd.DataFrame({"x1": all_pairs[:, 0], "x2": all_pairs[:, 1]})
    # get predictions
    z_pred_x1x2 = tree_filtering.predict(model, (0, 1), X_test)
    z_pred = model.predict(X_test, output_margin=True)  # vector

    # reshape Z3 vector into 2D numpy array for contour plotting (rows: x2, cols: x1)
    Z_Pred_x1x2 = z_pred_x1x2.reshape(len(x2), len(x1))

    # Z_Pred_x1x2
    contour_plot_Z_Pred_x1x2 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x1x2,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=start_val,
                end=stop_val,
                size=step_val,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )

    contour_plot_Z_Pred_x1x2.update_layout(
        title=f"Z_Pred_x1x2: {equation}",
        xaxis_title="x1",
        yaxis_title="x2",
    )

    contour_plot_Z_Pred_x1x2.show()


def plot_linear_one_var_xgbtrain(model, feature_names, equation):
    """
    model: xgb.Booster from xgb.train()
    feature_names: list of feature names, e.g. ['x1', 'x2']
    equation: string, for plot title
    """
    # Generate x_i vectors
    x_step = np.arange(0, 100, 0.1)
    x_random = np.random.uniform(0, 100, size=len(x_step))

    # Pandas DataFrames
    X_test1 = pd.DataFrame({feature_names[0]: x_step, feature_names[1]: x_random})
    X_test2 = pd.DataFrame({feature_names[0]: x_random, feature_names[1]: x_step})

    # Convert to DMatrix for xgb.train
    dtest1 = xgb.DMatrix(X_test1)
    dtest2 = xgb.DMatrix(X_test2)

    # Get predicted values
    model_x1 = purify.filter_save_load(model, (0,))
    model_x2 = purify.filter_save_load(model, (1,))
    y_pred_x1 = model_x1.predict(dtest1)
    y_pred_x2 = model_x2.predict(dtest2)

    # Plot
    plot = go.Figure()

    plot.add_trace(
        go.Scatter(
            x=X_test1[feature_names[0]],
            y=y_pred_x1,
            mode="lines",
            name=f"z_pred_{feature_names[0]}",
            line=dict(color="red"),
        )
    )

    plot.add_trace(
        go.Scatter(
            x=X_test2[feature_names[1]],
            y=y_pred_x2,
            mode="lines",
            name=f"z_pred_{feature_names[1]}",
            line=dict(color="blue"),
        )
    )

    plot.update_layout(
        title=f"{equation}",
        xaxis_title=f"{feature_names[0]}, {feature_names[1]}",
        yaxis_title="Predicted z",
    )

    plot.show()


def plot_contour_one_var_xgbtrain(
    model, feature_names, equation, start_val, stop_val, step_val
):
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    X_test = pd.DataFrame(
        {feature_names[0]: all_pairs[:, 0], feature_names[1]: all_pairs[:, 1]}
    )
    dtest = xgb.DMatrix(X_test)

    model_x1 = purify.filter_save_load(model, (0,))
    model_x2 = purify.filter_save_load(model, (1,))
    z_pred_x1 = model_x1.predict(dtest)
    z_pred_x2 = model_x2.predict(dtest)
    Z_Pred_x1 = z_pred_x1.reshape(len(x2), len(x1))
    Z_Pred_x2 = z_pred_x2.reshape(len(x2), len(x1))

    # Contour for x1
    fig1 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x1,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=start_val,
                end=stop_val,
                size=step_val,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )
    fig1.update_layout(
        title=f"Z_Pred_{feature_names[0]}: {equation}",
        xaxis_title=feature_names[0],
        yaxis_title=feature_names[1],
    )
    fig1.show()

    # Contour for x2
    fig2 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x2,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=start_val,
                end=stop_val,
                size=step_val,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )
    fig2.update_layout(
        title=f"Z_Pred_{feature_names[1]}: {equation}",
        xaxis_title=feature_names[0],
        yaxis_title=feature_names[1],
    )
    fig2.show()


def plot_contour_two_vars_xgbtrain(
    model, feature_names, equation, start_val, stop_val, step_val
):
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    X_test = pd.DataFrame(
        {feature_names[0]: all_pairs[:, 0], feature_names[1]: all_pairs[:, 1]}
    )
    dtest = xgb.DMatrix(X_test)

    model_x1x2 = purify.filter_save_load(model, (0, 1))
    z_pred_x1x2 = model_x1x2.predict(dtest)
    Z_Pred_x1x2 = z_pred_x1x2.reshape(len(x2), len(x1))

    fig = go.Figure(
        data=go.Contour(
            z=Z_Pred_x1x2,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=start_val,
                end=stop_val,
                size=step_val,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )
    fig.update_layout(
        title=f"Z_Pred_{feature_names[0]}{feature_names[1]}: {equation}",
        xaxis_title=feature_names[0],
        yaxis_title=feature_names[1],
    )
    fig.show()


###### TREE ADDITIVITY TESTS #####
def test_additivity_one_tree():
    """Test to see if prediction from summing predictions from individual trees (accounting for bias) equals prediction from original model"""

    # Generate 100 random samples sampled from normal distribution
    np.random.seed(42)
    x1 = np.random.randn(100)
    y = 10 * x1 + 10  # true function (no noise)

    # Split data into training and testing sets
    X = pd.DataFrame({"x1": x1})  # create tabular format of x1
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ###### FIT XGBOOST REGRESSOR ######

    # 3 trees of depth 1
    model = xgb.XGBRegressor(
        n_estimators=3,  # 3 tree
        max_depth=1,  # depth of 1
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.5,
    )
    model.fit(X_train, y_train)

    # y values predicted from entire default tree
    y_pred = model.predict(X_test, output_margin=True)
    y_pred_sum = tree_filtering.predict_sum_of_all_trees(model, X_test)

    # print(f"y_pred: {y_pred}")
    # print(f"y_pred_sum: {y_pred_sum}")
    assert np.allclose(np.round(y_pred, 3), np.round(y_pred_sum, 3))


def additivity_1_test(model):
    """
    model: XGB regressor model
    num_trees: string resembling equation we are fitting

    Returns True if adding up the predictions from each component (multiple predict functions) equals the original prediction

    """
    # Generate all combinations of pairs (x1, x2) from 0 too 100 in .1 increments
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    # convert all pairs to DataFrame structure
    X_test = pd.DataFrame({"x1": all_pairs[:, 0], "x2": all_pairs[:, 1]})
    # get predictions
    z_pred_x1 = tree_filtering.predict(model, (0,), X_test)
    z_pred_x2 = tree_filtering.predict(model, (1,), X_test)
    z_pred_x1x2 = tree_filtering.predict(model, (0, 1), X_test)
    z_pred_none = tree_filtering.predict(model, (), X_test)

    # reshape Z3 vector into 2D numpy array for contour plotting (rows: x2, cols: x1)
    bias = tree_filtering.get_bias(model)

    z_pred_sum = (
        z_pred_x1 + z_pred_x2 + z_pred_x1x2 + z_pred_none - 3 * bias
    )  # QUESTION ABOUT THIS (IS THIS OK??)
    z_pred = model.predict(X_test, output_margin=True)
    print(f"z_pred_sum{np.round(z_pred_sum[900:], 3)}")
    print(f"z_pred{np.round(z_pred[900:], 3)}")
    assert np.allclose(
        np.round(z_pred, 3), np.round(z_pred_sum, 3), atol=0.1
    ), "TEST_ADDITIVITY_1 FAILED"


def additivity_1_test_general(model):
    """
    model: xgb.Booster (from xgb.train)
    Returns True if adding up the predictions from each component (multiple filtered models) equals the original prediction.
    """
    # Generate all combinations of pairs (x1, x2) from 0 to 100 in 0.1 increments
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    X_test = pd.DataFrame({"x1": all_pairs[:, 0], "x2": all_pairs[:, 1]})
    dtest = xgb.DMatrix(X_test)

    # Get predictions from filtered models
    model_x1 = purify.filter_save_load(model, (0,))
    model_x2 = purify.filter_save_load(model, (1,))
    model_x1x2 = purify.filter_save_load(model, (0, 1))
    model_none = purify.filter_save_load(model, ())

    z_pred_x1 = model_x1.predict(dtest)
    z_pred_x2 = model_x2.predict(dtest)
    z_pred_x1x2 = model_x1x2.predict(dtest)
    z_pred_none = model_none.predict(dtest)

    # Get bias
    bias = purify.get_bias(model)

    # Additive sum (adjusting for bias counted in each component)
    z_pred_sum = z_pred_x1 + z_pred_x2 + z_pred_x1x2 + z_pred_none - 3 * bias

    # Original model prediction
    z_pred = model.predict(dtest)

    print(f"z_pred_sum{np.round(z_pred_sum[900:], 3)}")
    print(f"z_pred{np.round(z_pred[900:], 3)}")
    assert np.allclose(
        np.round(z_pred, 3), np.round(z_pred_sum, 3), atol=0.1
    ), "TEST_ADDITIVITY_1 FAILED"


###### TREE FILTER TESTS #####
def test_filter_two_vars_1():
    """
    test filtering of two_vars: y = 10 * x1 + 2 * x2
        No intercept
        Tree depth 1
        1000 trees
    """
    ##### GENERATE DATA #####
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2 * x2  # true function (no noise)
    # Split data into training (70%) and testing sets (30%)
    X = pd.DataFrame({"x1": x1, "x2": x2})  # create tabular format of x1, x2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ###### FIT XGBOOST REGRESSOR ######

    # Fit XGBoost regressor with 1000 trees of depth 1
    model = xgb.XGBRegressor(
        n_estimators=1000,  # 1000 trees
        max_depth=1,  # depth of 1
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.8,
    )
    model.fit(X_train, y_train)

    ###### PLOT ######
    plot_linear_one_var(model, "y = 10 * x1 + 2 * x2")


def test_filter_two_vars_2():
    """
    y = 10 * x1 + 2 * x2 + intercept

    Nonzero intercept
    Tree depth 2
    Contour Plot

    Total num trees: 1000
        num x2 trees: 149
        nm x2 trees: 96
        num x1x2 trees: 755
    """
    ##### GENERATE DATA #####
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2 * x2 + 5
    X = pd.DataFrame({"x1": x1, "x2": x2})  # create tabular format of x1, x2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ##### FIT REGRESSOR #####
    model = xgb.XGBRegressor(
        n_estimators=1000,  # 1000 trees
        max_depth=2,  # max_depth of 2
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.5,
    )
    model.fit(X_train, y_train)

    # TESTS
    additivity_1_test(model)

    ##### PLOT #####
    # test_additivity_2(model)

    # z_pred_x1, z_pred_x2
    plot_linear_one_var(model, "z = 10 * x1 + 2 * x2 + 5")
    plot_contour_one_var(model, "z = 10 * x1 + 2 * x2 + 5", -200, 200, 20)

    # z_pred_x1x2
    plot_contour_two_vars(model, "z = 10 * x1 + 2 * x2 + 5", -200, 200, 20)


def test_filter_two_vars_3():
    """
    y = 10x1 + 5x1x2 + 3
        1000 Trees --- Depth 2
    """
    ##### Generate Data #####
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 5 * x1 * x2 + 3
    X = pd.DataFrame({"x1": x1, "x2": x2})  # create tabular format of x1, x2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ##### FIT REGRESSOR  #####
    model = xgb.XGBRegressor(
        n_estimators=1000,  # 1000 trees
        max_depth=2,  # max_depth of 2
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.5,
    )
    model.fit(X_train, y_train)

    # TESTS
    additivity_1_test(model)

    ##### GENERATE PREDICTIONS #####
    plot_linear_one_var(model, "y = 10x1 + 5x1x2 + 3")
    plot_contour_one_var(model, "z = 10 * x1 + 2 * x2 + 5", -200, 200, 20)

    plot_contour_two_vars(model, "y = 10x1 + 5x1x2 + 3", -5000, 55000, 5000)


def test_filter_two_vars_4():
    """
    y = 10 * x1 + 5 * x1 * x2 + 3
        WITH CORRELATION BETWEEN x1/x2
    Unsure about plots but i'll take it for now.
    """
    ##### GENERATE DATA #####
    np.random.seed(42)

    # Specify means and covariance matrix
    mean = [0, 0]  # Means for x1 and x2
    corr = 0  # Desired correlation between x1 and x2 (rho)
    std_x1 = 1  # Standard deviation for x1
    std_x2 = 1  # Standard deviation for x2

    # Covariance matrix
    cov = [[std_x1**2, corr * std_x1 * std_x2], [corr * std_x1 * std_x2, std_x2**2]]

    # Generate correlated normal data
    x1, x2 = np.random.multivariate_normal(mean, cov, 1000).T

    # True y-val
    y = 10 * x1 + 5 * x1 * x2 + 3

    # Prepare DataFrame and split
    X = pd.DataFrame({"x1": x1, "x2": x2})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ##### FIT REGRESSOR #####
    model = xgb.XGBRegressor(
        n_estimators=1000,
        max_depth=2,  # 1
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.8,
    )
    model.fit(X_train, y_train)

    ##### TESTS #####
    additivity_1_test(model)

    ##### PLOTTING #####
    # For x1 effect: vary x1, randomize x2 (from correlated normal)
    x1_step = np.linspace(x1.min(), x1.max(), 500)
    x2_random = np.random.choice(x2, size=len(x1_step), replace=True)
    X_test1 = pd.DataFrame({"x1": x1_step, "x2": x2_random})

    # For x2 effect: vary x2, randomize x1 (from correlated normal)
    x2_step = np.linspace(x2.min(), x2.max(), 500)
    x1_random = np.random.choice(x1, size=len(x2_step), replace=True)
    X_test2 = pd.DataFrame({"x1": x1_random, "x2": x2_step})

    # Assuming you have a trained model and tree_filtering.predict
    z_pred_x1 = tree_filtering.predict(model, (0,), X_test1)
    z_pred_x2 = tree_filtering.predict(model, (1,), X_test2)

    plot = go.Figure()

    plot.add_trace(
        go.Scatter(
            x=X_test1["x1"],
            y=z_pred_x1,
            mode="markers",
            name="z_pred_x1",
            marker=dict(color="red"),
        )
    )

    plot.add_trace(
        go.Scatter(
            x=X_test2["x2"],
            y=z_pred_x2,
            mode="markers",
            name="z_pred_x2",
            marker=dict(color="blue"),
        )
    )

    plot.update_layout(
        title="Predicted z vs x1 and x2 (Correlated Normals)",
        xaxis_title="x1 or x2",
        yaxis_title="Predicted z",
    )
    plot.show()
    plot_contour_two_vars(model, "y = 10x1 + 5x1x2 + 5", 0, 50, 10)

    # #### PLOT 2D LINES #####
    # x_ver1 = np.arange(0, 100, 0.01)  # 0.1 step, not including 100
    # x_ver2 = np.random.uniform(0, len(x_ver1), size=len(x_ver1))
    # # X_test1 = pd.DataFrame({"x1": x1, "x2": x2})
    # X_test1 = pd.DataFrame({"x1": x_ver1, "x2": x_ver2})
    # # X_test2 = pd.DataFrame({"x1": x1, "x2": x2})
    # X_test2 = pd.DataFrame({"x1": x_ver2, "x2": x_ver1})
    # # o
    # z_pred_x1 = tree_filtering.predict(model, (0,), X_test1)
    # z_pred_x2 = tree_filtering.predict(model, (1,), X_test2)

    # x1_plot = px.scatter(
    #     x=X_test1["x1"],
    #     y=z_pred_x1,
    #     title="Predicted z vs x1",
    #     labels={"x": "x", "y": "Predicted z"},
    # )
    # x1_plot.show()

    # x2_plot = px.scatter(
    #     x=X_test1["x2"],
    #     y=z_pred_x2,
    #     title="Predicted z vs x2",
    #     labels={"x": "x", "y": "Predicted z"},
    # )
    # x2_plot.show()


def test_filter_two_vars_5():
    """
    y = log(x1 * x2)
        1000 Trees --- depth 2
    """
    ##### Generate Data #####
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = np.log(x1 * x2)
    X = pd.DataFrame({"x1": x1, "x2": x2})  # create tabular format of x1, x2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ##### FIT REGRESSOR  #####
    model = xgb.XGBRegressor(
        n_estimators=1000,  # 1000 trees
        max_depth=2,  # max_depth of 2
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.5,
    )
    model.fit(X_train, y_train)

    # TESTS
    additivity_1_test(model)

    ##### GENERATE PREDICTIONS AND PLOT #####
    plot_linear_one_var(model, "y = log(x1 * x2)")
    plot_contour_one_var(model, "y = log(x1 * x2)", -10, 10, 2)

    plot_contour_two_vars(model, "y = log(x1 * x2)", -6, 10, 2)

    """
    y = 10x1 + 8x2 + 7x3 + 2x1x2 + 9x1x3 + 3
        1000 Trees ---- depth 2
    """
    ##### GENERATE DATA #####
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    x3 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 8 * x2 + 7 * x3 + 2 * x1 * x2 + 9 * x1 * x3 + 3
    X = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ##### FIT REGRESSOR #####
    model = xgb.XGBRegressor(
        n_estimators=1000,  # 1000 trees
        max_depth=2,  # max_depth of 2
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.5,
    )
    model.fit(X_train, y_train)


###### TREE SAVING TESTS ######

# model for these tests
# Generate 1000 random vars sampled from uniform distribution
np.random.seed(42)
x1 = np.random.uniform(0, 100, 1000)
x2 = np.random.uniform(0, 100, 1000)
y = 10 * x1 + 2 * x2 + 5  # true function (no noise)

# Split data into training (70%) and testing sets (30%)
X = pd.DataFrame({"x1": x1, "x2": x2})  # create tabular format of x1, x2
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Fit XGboost regressor
test_filter_and_save_model = xgb.XGBRegressor(
    n_estimators=1000,  # 1000 trees
    max_depth=2,  # depth of 2
    learning_rate=1.0,
    objective="reg:squarederror",
    random_state=42,
    base_score=0.8,
)
test_filter_and_save_model.fit(X_train, y_train)


def test_filter_and_save_1():
    """
    y = 10 * x1 + 2 * x2
        1000 trees
        depth 1
    check if summing trees with x1 and trees with x2  (accounting for bias) is equivalent to original prediction model
        ADDITIVITY TEST: Returns True if adding up the predictions from each component (multiple predict functions) equals the original prediction
    """
    # Generate all combinations of pairs (x1, x2) from 0 too 100 in .1 increments
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    # convert all pairs to DataFrame structure
    X_test = pd.DataFrame({"x1": all_pairs[:, 0], "x2": all_pairs[:, 1]})

    ###### FILTER_AND_SAVE METHOD ######
    output_models = tree_filtering.filter_save_load(
        test_filter_and_save_model,
        [
            "test_filter_and_save_2_x1.json",
            "test_filter_and_save_2_x2.json",
            "test_filter_and_save_2_x1x2.json",
        ],
        [(0,), (1,), (0, 1)],
    )

    bias = tree_filtering.get_bias(test_filter_and_save_model)

    z_pred_sum_filter_and_save = -2 * bias
    for model in output_models:
        z_pred_sum_filter_and_save += model.predict(X_test, output_margin=True)

    ###### BUILT IN METHOD ######
    z_pred = test_filter_and_save_model.predict(X_test, output_margin=True)

    ###### EQUALITY TEST ######
    assert np.allclose(
        np.round(z_pred, 3), np.round(z_pred_sum_filter_and_save, 3), atol=0.1
    )


def test_filter_and_save_2():
    """
    y = 10 * x1 + 2 * x2 + 5
        1000 trees
        depth 2
    check if prediction from each term f(x1), f(x2), f(x1x2) (on the saved file) equals the prediction from our original filters using "iteration_range"
        EQUALITY TEST
    """
    bias = tree_filtering.get_bias(test_filter_and_save_model)

    ###### ITERATION_RANGE METHOD ######
    z_pred_x1 = tree_filtering.predict(test_filter_and_save_model, (0,), X_test)
    z_pred_x2 = tree_filtering.predict(test_filter_and_save_model, (1,), X_test)
    z_pred_x1x2 = tree_filtering.predict(test_filter_and_save_model, (0, 1), X_test)
    z_pred_sum_iteration_range = z_pred_x1 + z_pred_x2 + z_pred_x1x2 - 2 * bias

    ###### FILTER_AND_SAVE METHOD ######
    output_models = tree_filtering.filter_save_load(
        test_filter_and_save_model,
        [
            "test_filter_and_save_2_x1.json",
            "test_filter_and_save_2_x2.json",
            "test_filter_and_save_2_x1x2.json",
        ],
        [(0,), (1,), (0, 1)],
    )

    z_pred_sum_filter_and_save = -2 * bias
    for model in output_models:
        z_pred_sum_filter_and_save += model.predict(X_test, output_margin=True)

    # print(f"z_pred_sum_iteration_range: {z_pred_sum_iteration_range[:10]}")
    # print(f"z_pred_sum_filter_and_save: {z_pred_sum_filter_and_save[:10]}")

    assert np.allclose(
        np.round(z_pred_sum_iteration_range, 3),
        np.round(z_pred_sum_filter_and_save, 3),
        atol=0.1,
    )


def test_filter_and_save_3():
    """
    test filtering of two_vars: y = 10 * x1 + 2 * x2
        No intercept
        Tree depth 1
        1000 trees
    by graphing (like test_filter_two_vars_1 but using this saving method)
    """
    ##### GENERATE DATA AND FIT REGRESSOR #####
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2 * x2  # true function (no noise)
    # Split data into training (70%) and testing sets (30%)
    X = pd.DataFrame({"x1": x1, "x2": x2})  # create tabular format of x1, x2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Fit XGBoost regressor with 1000 trees of depth 1
    model = xgb.XGBRegressor(
        n_estimators=1000,  # 1000 trees
        max_depth=2,  # depth of 2
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.8,
    )
    model.fit(X_train, y_train)

    ###### 2D PLOT ######
    # Generate x_i vectors
    x_step = np.arange(0, 100, 0.1)  # 0.1 step, not including 100
    x_random = np.random.uniform(0, 100, size=len(x_step))

    # Pandas Dataframes
    X_test1 = pd.DataFrame({"x1": x_step, "x2": x_random})
    X_test2 = pd.DataFrame({"x1": x_random, "x2": x_step})

    # Get predicted values
    individual_models = tree_filtering.filter_save_load(
        model,
        [
            "test_filter_and_save_3_x1.json",
            "test_filter_and_save_3_x2.json",
            "test_filter_and_save_3_x1x2.json",
        ],
        [(0,), (1,), (0, 1)],
    )

    z_pred_x1 = individual_models[0].predict(X_test1)
    z_pred_x2 = individual_models[1].predict(X_test2)

    plot = go.Figure()

    plot.add_trace(
        go.Scatter(
            x=X_test1["x1"],
            y=z_pred_x1,
            mode="lines",
            name="z_pred_x1",
            line=dict(color="red"),  # specify color here
        )
    )

    plot.add_trace(
        go.Scatter(
            x=X_test2["x2"],
            y=z_pred_x2,
            mode="lines",
            name="z_pred_x2",
            line=dict(color="blue"),  # different color here
        )
    )

    plot.update_layout(
        title=f"y = 10 * x1 + 2 * x2", xaxis_title="x1, x2", yaxis_title="Predicted z"
    )

    plot.show()

    ###### CONTOUR PLOT ######

    # Generate all combinations of pairs (x1, x2) from 0 too 100 in .1 increments
    x1 = np.arange(0, 100, 0.1)
    x2 = np.arange(0, 100, 0.1)
    X1, X2 = np.meshgrid(x1, x2)
    all_pairs = np.column_stack([X1.flatten(), X2.flatten()])
    # convert all pairs to DataFrame structure
    X_test = pd.DataFrame({"x1": all_pairs[:, 0], "x2": all_pairs[:, 1]})

    z_pred_x1 = individual_models[0].predict(X_test)
    z_pred_x2 = individual_models[1].predict(X_test)
    z_pred_x1x2 = individual_models[2].predict(X_test)

    Z_Pred_x1 = z_pred_x1.reshape(len(x2), len(x1))
    Z_Pred_x2 = z_pred_x2.reshape(len(x2), len(x1))
    Z_Pred_x1x2 = z_pred_x1x2.reshape(len(x2), len(x1))

    # Z_Pred_x1
    contour_plot_Z_Pred_x1 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x1,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=0,
                end=1000,
                size=10,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )

    contour_plot_Z_Pred_x1.update_layout(
        title=f"Z_Pred_x1: y = 10 * x1 + 2 * x2",
        xaxis_title="x1",
        yaxis_title="x2",
    )

    contour_plot_Z_Pred_x1.show()

    # Z_Pred_x12
    contour_plot_Z_Pred_x2 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x2,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=0,
                end=100,
                size=10,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )

    contour_plot_Z_Pred_x2.update_layout(
        title=f"Z_Pred_x2: y = 10 * x1 + 2 * x2",
        xaxis_title="x1",
        yaxis_title="x2",
    )

    contour_plot_Z_Pred_x2.show()

    # Z_Pred_x1x2
    contour_plot_Z_Pred_x1x2 = go.Figure(
        data=go.Contour(
            z=Z_Pred_x1x2,
            x=x1,
            y=x2,
            colorscale="sunset",
            contours=dict(
                start=-200,
                end=200,
                size=25,
                coloring="heatmap",
                showlabels=True,
            ),
            line=dict(width=2),
            colorbar=dict(title="Z value"),
        )
    )

    contour_plot_Z_Pred_x1x2.update_layout(
        title=f"Z_Pred_x1x2: y = 10 * x1 + 2 * x2",
        xaxis_title="x1",
        yaxis_title="x2",
    )

    contour_plot_Z_Pred_x1x2.show()


###### TREE ADDING TESTS ######
def test_tree_centering_1():
    """Test if fatter taller prediction equals original prediciton"""
    # Initialization
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)  # 1000 test points
    y = 10 * x1 + 2

    X = pd.DataFrame({"x1": x1})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = xgb.XGBRegressor(
        n_estimators=1000,  # 100 trees
        max_depth=1,  # depth of 1
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.8,
    )
    model.fit(X_train, y_train)

    # Test similarity
    tree_filtering.save_new_model_depth_1_two_vars_additional_tree(
        model, X_test, "model_one_var_centered.json"
    )
    model_one_var_centered = xgb.XGBRegressor()
    model_one_var_centered.load_model("model_one_var_centered.json")
    y_pred_centered = model_one_var_centered.predict(X_test)
    y_pred = model.predict(X_test)

    assert np.allclose(np.round(y_pred, 3), np.round(y_pred_centered, 3), atol=0.1)


##### RANDOM GENERATORS #####
def general_generator():
    ####### GENERATE DATA #######
    # Generate 1000 random vars sampled from uniform distribution
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2 * x2  # true function (no noise)

    # Split data into training (70%) and testing sets (30%)
    X = pd.DataFrame({"x1": x1, "x2": x2})  # create tabular format of x1, x2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    ###### FIT XGBOOST REGRESSOR ######
    model = xgb.XGBRegressor(
        n_estimators=10,  # 1000 trees
        max_depth=1,  # depth of 1
        learning_rate=1.0,
        objective="reg:squarederror",
        random_state=42,
        base_score=0.8,
    )
    model.fit(X_train, y_train)
    # model.save_model("model_example_1_trees_d2.json")

    y_true = y_test  # True y vals
    # y value predicted from entire default tree
    y_pred = model.predict(X_test, output_margin=True)
    y_pred_x1 = tree_filtering.predict(model, (0,), X_test)
    y_pred_x1 = tree_filtering.predict(model, (1,), X_test)

    # y value predicted from summing individual trees
    trees_feature_x1 = tree_filtering.get_filtered_tree_list_ranges_from_tuple(
        model, (0,)
    )
    trees_feature_x2 = tree_filtering.get_filtered_tree_list_ranges_from_tuple(
        model, (1,)
    )
    print(f"trees_with_feature_x1: {trees_feature_x1}")
    print(f"trees_with_feature_x2: {trees_feature_x2}")

    # # "reasonability" check
    # filter_and_save(model, "test_model_10_trees_x1", (0,))
    # filter_and_save(model, "test_model_10_trees_x2", (1,))
    # assert os.path.exists("test_model_10_trees_x2.json"), "File not created!"

    # # prediction check
    # new_model = xgb.XGBRegressor()
    # new_model.load_model("test_model_10_trees_x2.json")
    # new_model.load_model("test_model_10_trees_x1.json")

    # # After saving
    # print(new_model.predict(X_test))


##### GENERAL TRAIN TESTS (for filter.py) #####
def test_general_1():
    """ADDITIVITY"""
    # Generate data
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2 * x2 + 5
    X = pd.DataFrame({"x1": x1, "x2": x2})
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Fit XGBoost using xgb.train
    dtrain = xgb.DMatrix(X_train, label=y_train)
    params = {
        "max_depth": 2,
        "eta": 1.0,
        "objective": "reg:squarederror",
        "base_score": 0.5,
        "seed": 42,
    }
    model = xgb.train(params, dtrain, num_boost_round=1000)

    # Run additivity test
    additivity_1_test_general(model)


def test_general_2():
    """SIMPLE FILTERING"""
    # Data generation and training with xgb.train()
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2 * x2

    X = pd.DataFrame({"x1": x1, "x2": x2})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    dtrain = xgb.DMatrix(X_train, label=y_train)
    params = {
        "max_depth": 1,
        "eta": 1.0,
        "objective": "reg:squarederror",
        "base_score": 0.8,
        "seed": 42,
    }
    model = xgb.train(params, dtrain, num_boost_round=1000)

    # Plot
    plot_linear_one_var_xgbtrain(model, ["x1", "x2"], "y = 10 * x1 + 2 * x2")


def test_general_3():
    """3D FILTERING"""
    # Generate data
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    x2 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2 * x2 + 5
    X = pd.DataFrame({"x1": x1, "x2": x2})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Fit XGBoost with xgb.train
    dtrain = xgb.DMatrix(X_train, label=y_train)
    params = {
        "max_depth": 2,
        "eta": 1.0,
        "objective": "reg:squarederror",
        "base_score": 0.5,
        "seed": 42,
    }
    model = xgb.train(params, dtrain, num_boost_round=1000)

    # Plotting
    plot_linear_one_var_xgbtrain(model, ["x1", "x2"], "z = 10 * x1 + 2 * x2 + 5")
    plot_contour_one_var_xgbtrain(
        model, ["x1", "x2"], "z = 10 * x1 + 2 * x2 + 5", -200, 200, 20
    )
    plot_contour_two_vars_xgbtrain(
        model, ["x1", "x2"], "z = 10 * x1 + 2 * x2 + 5", -200, 200, 20
    )


def test_general_4():
    """CENTERING"""
    # Generate simple data
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 1000)
    y = 10 * x1 + 2
    X = pd.DataFrame({"x1": x1})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Train with xgb.train
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test)
    params = {
        "max_depth": 1,
        "eta": 1.0,
        "objective": "reg:squarederror",
        "base_score": 0.8,
        "seed": 42,
    }
    model = xgb.train(params, dtrain, num_boost_round=1000)

    # Get original predictions and mean
    y_pred = model.predict(dtest)
    mean_pred = np.mean(y_pred)
    original_base_score = filter.get_bias(model)
    new_base_score = round(float(mean_pred) + original_base_score, 6)
    new_base_score_str = "{:.6f}".format(new_base_score)

    # Call save_load_new_trees to add a tree with leaf value -mean_pred and update base_score
    new_model = filter.save_load_new_trees(
        model,
        leaf_val=-mean_pred,
        base_score=new_base_score_str,
        num_new_trees=1,
        output_file_name="model_one_var_centered.json",
        folder="loaded_models",
    )

    # Predict with the new model
    y_pred_centered = new_model.predict(dtest)

    # Assert predictions are close
    assert np.allclose(
        np.round(y_pred, 3), np.round(y_pred_centered, 3), atol=0.1
    ), "TEST_SAVE_LOAD_NEW_TREES FAILED"


##### PURIFICATION TESTS #####
def test_purification_1():
    """5 Nodes"""
    np.random.seed(42)
    x1 = np.random.uniform(0, 100, 10)
    x2 = np.random.uniform(0, 100, 10)
    y = 10 * x1 + 2 * x2 + 3 * x1 * x2 + 5

    X = pd.DataFrame({"x1": x1, "x2": x2})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Convert to DMatrix format required by xgb.train
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    # Parameters (note different parameter names)
    params = {
        "max_depth": 2,
        "learning_rate": 1.0,
        "objective": "reg:squarederror",
        "random_state": 42,
    }

    # Training with monitoring
    model = xgb.train(
        params=params,
        dtrain=dtrain,
        num_boost_round=5,  # Equivalent to n_estimators
        evals=[(dtrain, "train"), (dtest, "test")],
        verbose_eval=True,
    )

    new_model = purify.filter_save_load(model, (0, 1), "original_model.json")
    print(f"original_prediction: {new_model.predict(dtest)}")
    purified_new_model = purify.fANOVA_2D(new_model, dtest)
    print(f"purified_prediction: {purified_new_model.predict(dtest)}")


if __name__ == "__main__":
    pass
