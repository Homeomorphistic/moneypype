import sys
from streamlit.web import cli as stcli

import moneypype.console as console


def main() -> None:
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())


if __name__ == "__main__":
    import streamlit as st

    st.title("moneypype")

    source = st.text_input("Source file")
    dest = st.text_input("Output directory", value=console.default_dest())
    categories_map = st.text_input("Categories map", value=console.default_map())

    if st.button("Run"):
        try:
            df = console.run(source, dest, categories_map)
            st.success(f"Saved to {dest}")
            st.dataframe(df.head(20))
        except Exception as e:
            st.error(e.args[0])
