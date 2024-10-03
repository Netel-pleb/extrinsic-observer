

import sentry_sdk

# Initialize Sentry
sentry_sdk.init(
    dsn="https://6e3a37317c95479be36f956c3d8b4838@o4508058871463936.ingest.us.sentry.io/4508058885357568",  # Replace with your Sentry DSN
)

def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        # Capture the exception in Sentry
        sentry_sdk.capture_exception(e)
        return "Error: Division by zero!"

if __name__ == "__main__":
    print(divide(10, 2))  # This will work
    print(divide(10, 0))  # This will trigger an error
