import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest

# Load the logs
log_file = "C:\\EventTrackAi\\event_logs.csv"
df = pd.read_csv(log_file, encoding="utf-8")

# Select relevant columns (adjust based on your log format)
df = df[['Id', 'Level', 'Message']]  # Keep only useful fields

# Convert text messages into numerical features
vectorizer = TfidfVectorizer(max_features=100)
X_text = vectorizer.fit_transform(df["Message"].astype(str)).toarray()

# Combine numeric and text features
X = pd.concat([df[['Id']], pd.DataFrame(X_text)], axis=1)

# Convert all column names to strings
X.columns = X.columns.astype(str)

# Train an anomaly detection model
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X)

# Predict anomalies
df["Anomaly"] = model.predict(X)

# Mark suspicious events
df["Anomaly"] = df["Anomaly"].map({1: "Normal", -1: "Suspicious"})

# Show results
print(df[df["Anomaly"] == "Suspicious"])
