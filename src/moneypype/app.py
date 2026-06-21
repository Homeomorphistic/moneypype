import sys
from streamlit.web import cli as stcli


def main() -> None:
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())


if __name__ == "__main__":
    import streamlit as st

    st.title("moneypype")
    st.write("Pipeline UI coming soon.")
