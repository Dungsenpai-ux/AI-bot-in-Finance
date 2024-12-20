# -*- coding: utf-8 -*-
"""lstm_stock_predictor_closing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1BFfoYXUGoTJOc1CCS40BFxMZFt3XrFUl
"""

import numpy as np
import pandas as pd
import hvplot.pandas
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

# Set the random seed for reproducibility
from numpy.random import seed
seed(1)
from tensorflow import random
random.set_seed(2)

# Load the fear and greed sentiment data for Bitcoin
df = pd.read_csv('data.csv', index_col="date", infer_datetime_format=True, parse_dates=True)
df = df.drop(columns="fng_classification")
df.head()

# Load the historical closing prices for Bitcoin
df2 = pd.read_csv('ETH_historic.csv', index_col="Date", infer_datetime_format=True, parse_dates=True)['Close']
df2 = df2.sort_index()
df2.tail()

print(df.dtypes)

common_dates = df.index.intersection(df2.index)
print("Common dates:", common_dates)

df.index = pd.to_datetime(df.index, dayfirst=True)
df2.index = pd.to_datetime(df2.index, dayfirst=True)

print(df.dtypes)

# Join the data into a single DataFrame
df = df.join(df2, how="inner")
df.tail()

df.head()

# It returns a numpy array of X any y
def window_data(df, window, feature_col_number, target_col_number):
    X = []
    y = []
    for i in range(len(df) - window - 1):
        features = df.iloc[i:(i + window), feature_col_number]
        target = df.iloc[(i + window), target_col_number]
        X.append(features)
        y.append(target)
    return np.array(X), np.array(y).reshape(-1, 1)

# Predict Closing Prices using a 1 day window of previous closing prices
window_size = 1

# Column index 0 is the 'fng_value' column
# Column index 1 is the `Close` column
feature_column = 1
target_column = 1
X, y = window_data(df, window_size, feature_column, target_column)

# Use 70% of the data for training and the remaineder for testing
split = int(0.7 * len(X))
X_train = X[: split]
X_test = X
y_train = y[: split]
y_test = y

# Use the MinMaxScaler to scale data between 0 and 1.
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaler.fit(X)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

scaler.fit(y)

y_train = scaler.transform(y_train)
y_test = scaler.transform(y_test)

# Reshape the features for the model
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))


# Define the LSTM RNN model.
model = Sequential()

number_units = 50
dropout_fraction = 0.2

# Layer 1
model.add(LSTM(
    units=number_units,
    return_sequences=True,
    input_shape=(X_train.shape[1], 1))
    )
model.add(Dropout(dropout_fraction))
# Layer 2
model.add(LSTM(units=number_units, return_sequences=True))
model.add(Dropout(dropout_fraction))
# Layer 3
model.add(LSTM(units=number_units))
model.add(Dropout(dropout_fraction))
# Output layer
model.add(Dense(1))

# Compile the model
model.compile(optimizer="adam", loss="mean_squared_error")

# Summarize the model
model.summary()

# Train the model
history = model.fit(X_train, y_train, epochs=15, shuffle=False, batch_size=1, verbose=1)

"""## Model Performance"""

# Evaluate the model
model.evaluate(X_test, y_test)
len(X_test)

# Make some predictions
predicted = model.predict(X_test)

# Recover the original prices instead of the scaled version
predicted_prices = scaler.inverse_transform(predicted)
real_prices = scaler.inverse_transform(y_test.reshape(-1, 1))

# Create a DataFrame of Real and Predicted values
stocks = pd.DataFrame({
    "Real": real_prices.ravel(),
    "Predicted": predicted_prices.ravel()
}, index = df.index[-len(real_prices):])
stocks.head()

stocks.hvplot()

# Plot real vs predicted closing prices on the test set
plt.figure(figsize=(14, 7))

# Plot real prices
plt.plot(df.index[-len(real_prices):], real_prices, label="Real Prices", color='blue')

# Plot predicted prices
plt.plot(df.index[-len(predicted_prices):], predicted_prices, label="Predicted Prices", color='red', linestyle='--')

plt.title("Real vs Predicted Bitcoin Closing Prices", fontsize=16)
plt.xlabel("Date", fontsize=14)
plt.ylabel("Price (USD)", fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

# Hàm tải và xử lý dữ liệu
def load_data(file_path):
    data = pd.read_csv(file_path)
    data = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    return scaled_data, scaler

# Chuẩn bị tập dữ liệu cho LSTM
def prepare_data(data, time_step=60):
    X, y = [], []
    for i in range(time_step, len(data)):
        X.append(data[i-time_step:i, 0])
        y.append(data[i, 0])
    X = np.array(X)
    y = np.array(y)
    return X.reshape(X.shape[0], X.shape[1], 1), y

# Xây dựng mô hình LSTM
def build_lstm(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Ứng dụng Streamlit
st.title("Dự đoán giá cổ phiếu bằng LSTM")
uploaded_file = st.file_uploader("ETH_historic.csv", type=["csv"])

if uploaded_file is not None:
    # Xử lý dữ liệu
    scaled_data, scaler = load_data(uploaded_file)
    train_size = int(len(scaled_data) * 0.8)
    train_data, test_data = scaled_data[:train_size], scaled_data[train_size:]
    time_step = 60
    X_train, y_train = prepare_data(train_data, time_step)
    X_test, y_test = prepare_data(test_data, time_step)

    # Huấn luyện mô hình
    st.write("Đang huấn luyện mô hình...")
    model = build_lstm((X_train.shape[1], 1))
    model.fit(X_train, y_train, batch_size=32, epochs=5, verbose=1)

    # Dự đoán
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    # Hiển thị biểu đồ
    st.subheader("Kết quả dự đoán")
    plt.figure(figsize=(12, 6))
    plt.plot(y_test_actual, label="Thực tế")
    plt.plot(predictions, label="Dự đoán")
    plt.legend()
    st.pyplot(plt)



