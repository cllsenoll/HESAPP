"Nakit Ödeme Tutarı Topl": st.column_config.NumberColumn("Nakit Ödeme Tutarı Topl", format="%.2f TL", disabled=True),
                "Banka/ATM": st.column_config.NumberColumn("Banka/ATM (Yatırılan)", format="%.2f TL", min_value=0.0, step=10.0),
                "Hesap": st.column_config.NumberColumn("Kalan Hesap", format="%.2f TL", disabled=True),
                "İşlem": st.column_config.CheckboxColumn("İşlem Tamam", default=False)
            },
            use_container_width=True,
            hide_index=True,
            key="hesap_data_editor"
        )

        # Düzenlenen değerleri anlık olarak hesapla ve güncelle
        edited_df["Hesap"] = edited_df["Nakit Ft Tutarı Topl"] + edited_df["Nakit Ödeme Tutarı Topl"] - edited_df["Banka/ATM"]
        st.session_state.hesap_df = edited_df

        st.markdown("---")
        st.subheader("💵 Kasa Kontrolü ve Fark Hesaplama")

        col_k1, col_k2 = st.columns([1, 2])
        with col_k1:
            girilen_kasa = st.number_input(
                "Şube Kasa Miktarı (TL):",
                min_value=0.0,
                value=float(st.session_state.kasa_miktari),
                step=50.0,
                format="%.2f",
                key="kasa_input_field"
            )
            st.session_state.kasa_miktari = girilen_kasa

        toplam_hesap_tutar = edited_df["Hesap"].sum()
        kasa_farki = girilen_kasa - toplam_hesap_tutar

        with col_k2:
            st.markdown("##### 📊 Kasa Durum Özeti")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Toplam Hesap", f"{toplam_hesap_tutar:,.2f} TL")
            m_col2.metric("Girilen Kasa", f"{girilen_kasa:,.2f} TL")
            
            if kasa_farki > 0:
                m_col3.metric("Kasa Durumu", f"FAZLA: {abs(kasa_farki):,.2f} TL", delta=f"+{kasa_farki:,.2f} TL", delta_color="normal")
            elif kasa_farki < 0:
                m_col3.metric("Kasa Durumu", f"AÇIK: {abs(kasa_farki):,.2f} TL", delta=f"{kasa_farki:,.2f} TL", delta_color="inverse")
            else:
                m_col3.metric("Kasa Durumu", "KASA TAM (0.00 TL)", delta="0.00 TL", delta_color="off")

        st.markdown("---")
        
        # PDF İndirme Butonu
        pdf_bytes_data = generate_hesap_pdf(edited_df, girilen_kasa)
        st.download_button(
            label="📄 Hesap Özetini ve Raporu PDF Olarak İndir",
            data=pdf_bytes_data,
            file_name="gorukle_gunluk_hesap_raporu.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    else:
        st.info("ℹ️ Lütfen sol paneldeki dosya yükleme alanından personel hesap listesini (nakit/ödeme raporunu) yükleyin.")

# ==========================================
# ANA EKRAN / F4 ÖDEME LİSTESİ TABI GÖSTERİMİ
# ==========================================
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.title("📋 F4 Ödeme ve Personel Tahsilat Listesi")
    st.caption("Bu ekrandan F4 borç listesini inceleyebilir, müşterilerin hangi personele ait olduğunu görebilir ve gerektiğinde personel ataması yapabilirsiniz.")

    f4_df = st.session_state.get("f4_df", None)

    if f4_df is not None and not f4_df.empty:
        if 'editable_f4_df' not in st.session_state or st.session_state.editable_f4_df is None:
            st.session_state.editable_f4_df = f4_df.copy()

        gercek_personeller = sorted([p for p in MUSTERI_PERSONEL_MAP.values() if p != "ATANMAMIŞ"])
        tum_personel_secenekleri = sorted(list(set(gercek_personeller + ["ATANMAMIŞ"] + list(st.session_state.editable_f4_df["Personel"].unique()))))

        tab_atanmamis, tab_tum, tab_filtre = st.tabs([
            "⚠️ ATANMAMIŞ Müşteriler & Atama Yap", 
            "📝 Tüm Listeyi Düzenle", 
            "🔍 Personele Göre Süzgeçli Görünüm"
        ])

        with tab_atanmamis:
            st.markdown("#### ⚠️ Henüz Personele Atanmamış Müşteri Listesi")
            st.caption("Aşağıdaki tabloda yalnızca 'ATANMAMIŞ' olan müşteriler yer alır. 'Atanacak Personel' sütunundan ismi seçerek ilgili müşteriyi doğrudan o personele atayabilirsiniz.")

            mask_atanmamis = (st.session_state.editable_f4_df["Personel"] == "ATANMAMIŞ") | (st.session_state.editable_f4_df["Personel"] == "")
            sub_atanmamis_df = st.session_state.editable_f4_df[mask_atanmamis].copy()

            if not sub_atanmamis_df.empty:
                edited_atanmamis_df = st.data_editor(
                    sub_atanmamis_df,
                    column_config={
                        "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                        "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f TL", disabled=True),
                        "Açıklama": st.column_config.TextColumn("Açıklama", disabled=True),
                        "Personel": st.column_config.SelectboxColumn(
                            "Atanacak Personel",
                            options=gercek_personeller,
                            required=True
                        )
                    },
                    use_container_width=True,
                    hide_index=True,
                    key="atanmamis_data_editor"
                )

                for idx in edited_atanmamis_df.index:
                    yeni_personel = edited_atanmamis_df.loc[idx, "Personel"]
                    st.session_state.editable_f4_df.loc[idx, "Personel"] = yeni_personel

                if st.button("💾 Atamaları Kaydet ve Güncelle"):
                    st.success("✅ Atamalar başarıyla güncellendi!")
                    st.rerun()
            else:
                st.info("🎉 Harika! Şu anda 'ATANMAMIŞ' durumunda hiçbir müşteri kalmadı.")

        with tab_tum:
            st.markdown("#### Tüm Müşteri ve Personel Atama Tablosu")
            
            col_kasa1, col_kasa2, col_kasa3 = st.columns(3)
            with col_kasa1:
                kops_kasa = st.number_input("KOPS KASA", value=0.0, format="%.2f", step=100.0)
            with col_kasa2:
                atm_yatirilacak = st.number_input("ATM yatırılacak", value=0.0, format="%.2f", step=100.0)
            with col_kasa3:
                devredecek = kops_kasa - atm_yatirilacak
                st.number_input("Devredecek", value=devredecek, format="%.2f", disabled=True)

            edited_f4_main = st.data_editor(
                st.session_state.editable_f4_df,
                column_config={
                    "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                    "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f TL", disabled=True),
                    "Açıklama": st.column_config.TextColumn("Açıklama", disabled=True),
                    "Personel": st.column_config.SelectboxColumn(
                        "Sorumlu Personel",
                        options=tum_personel_secenekleri,
                        required=True
                    )
                },
                use_container_width=True,
                hide_index=True,
                key="f4_main_data_editor"
            )
            st.session_state.editable_f4_df = edited_f4_main

        with tab_filtre:
            st.markdown("#### Personel Bazlı Tahsilat Süzgeci")
            secilen_personel_filtre = st.selectbox(
                "İncelemek İstediğiniz Personeli Seçin:",
                options=tum_personel_secenekleri,
                key="personel_selectbox_filter"
            )

            filtered_display_df = st.session_state.editable_f4_df[
                st.session_state.editable_f4_df["Personel"] == secilen_personel_filtre
            ]
            toplam_kayit = len(filtered_display_df)
            toplam_borc = filtered_display_df["Fatura Borcu"].sum()

            f_col1, f_col2 = st.columns(2)
            f_col1.metric("Toplam Müşteri Sayısı", toplam_kayit)
            f_col2.metric("Toplam Fatura Borcu", f"{toplam_borc:,.2f} TL")

            st.markdown("<br>", unsafe_allow_html=True)

            st.dataframe(
                filtered_display_df,
                column_config={
                    "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                    "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f TL", disabled=True),
                    "Açıklama": st.column_config.TextColumn("Açıklama", disabled=True),
                    "Personel": st.column_config.TextColumn("Personel", disabled=True)
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("ℹ️ Lütfen sol panelden F4 ödeme listesini yükleyin.")
