import streamlit as st


def render_results():
    links = st.session_state.get("generated_links")
    raw_blocks = st.session_state.get("raw_blocks")

    if links:
        st.success(f":tada: !کانفیگ با موفقیت استخراج شد {len(links)}")

        st.subheader(":clipboard: همه‌ی کانفیگ‌ها (یک‌جا برای کپی)")
        all_links_text = "\n".join(links)
        st.code(all_links_text, language="text")
        st.download_button(
            ":inbox_tray: (.txt) دانلود لینک‌ها به صورت یکجا",
            data=all_links_text,
            file_name="extracted_configs.txt",
            mime="text/plain",
        )

        with st.expander(f"({len(links)}) نمایش تک‌تک لینک‌ها"):
            for link in links:
                st.code(link, language="text")

    if raw_blocks:
        for idx, decoded_str in raw_blocks:
            with st.expander("اطلاعات بیشتر"):
                st.code(decoded_str, language="json")

    if links == [] and not raw_blocks:
        st.info(".هیچ کانفیگ قابل‌تبدیلی یافت نشد")

    plain = st.session_state.get("plain_decoded")
    if plain:
        st.success(":white_check_mark: :نتیجه")
        st.code(plain, language="text")
