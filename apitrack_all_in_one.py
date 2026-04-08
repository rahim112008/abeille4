# ─────────────────────────────────────────────
# SIDEBAR (avec nouvel onglet "Cartographie")
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 20px">
        <div style="background:linear-gradient(135deg,#D4820A,#8B5200);border-radius:14px;
                    width:52px;height:52px;display:flex;align-items:center;justify-content:center;
                    font-size:26px;margin-bottom:12px">🐝</div>
        <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;
                    color:#F5C842;line-height:1.1">ApiTrack Pro</div>
        <div style="font-size:10px;letter-spacing:0.14em;text-transform:uppercase;
                    color:rgba(255,255,255,0.45);margin-top:3px">Plateforme Apicole v2.0</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    pages = {
        "📊 Vue d'ensemble": "dashboard",
        "🏠 Mes Ruches": "ruches",
        "🔍 Inspections": "inspections",
        "💊 Traitements": "traitements",
        "🍯 Miel": "miel",
        "🌼 Pollen": "pollen",
        "👑 Gelée Royale": "gelee",
        "🔬 Morphométrie": "morphometrie",
        "🧬 Génétique & Races": "genetique",
        "📈 Caractérisation": "caracterisation",
        "🗺️ Cartographie": "carte",
        "🌸 Flore Mellifère": "flore",
        "🌤️ Météo & Miellée": "meteo",
        "📋 Rapports": "rapports",
        "🚨 Alertes": "alertes",
        "💾 Administration": "admin",
    }

    selected_label = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    current_page = pages[selected_label]

    st.markdown("<hr>", unsafe_allow_html=True)
    nb_ruches = len(st.session_state.data["ruches"])
    nb_alertes = len(st.session_state.data["ruches"][st.session_state.data["ruches"]["Statut"].isin(["Critique","Attention"])])
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:14px 16px;font-size:12px">
        <div style="color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.1em;
                    font-size:10px;margin-bottom:8px">Aperçu rapide</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:rgba(255,255,255,0.7)">🏠 Ruches actives</span>
            <strong style="color:#F5C842">{nb_ruches}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:rgba(255,255,255,0.7)">🚨 Alertes</span>
            <strong style="color:#ef4444">{nb_alertes}</strong>
        </div>
        <div style="display:flex;justify-content:space-between">
            <span style="color:rgba(255,255,255,0.7)">🍯 Total miel</span>
            <strong style="color:#F5C842">{st.session_state.data['ruches']['Miel_kg'].sum():.0f} kg</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:auto;padding-top:20px;display:flex;align-items:center;gap:10px">
        <div style="width:36px;height:36px;background:#D4820A;border-radius:50%;
                    display:flex;align-items:center;justify-content:center;font-weight:700;
                    color:#2D4A1E;font-size:14px;flex-shrink:0">{st.session_state.apiculteur[0] if st.session_state.apiculteur else 'A'}</div>
        <div>
            <div style="font-size:13px;color:rgba(255,255,255,0.85);font-weight:500">{st.session_state.apiculteur}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.4)">Apiculteur professionnel</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: ADMINISTRATION (corrigée sans erreur d'indentation)
# ─────────────────────────────────────────────
if current_page == "admin":
    st.markdown('<div class="page-title">💾 Administration</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Sauvegarde, restauration, gestion des ruches et profil</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["💾 Sauvegarde / Restauration", "🗑 Supprimer une ruche", "👤 Profil apiculteur", "🔐 Sécurité"])
    
    with tab1:
        st.markdown("#### Sauvegarder la base de données")
        if st.button("📥 Préparer le téléchargement de la base"):
            with open(DB_PATH, "rb") as f:
                st.download_button(
                    label="Cliquez pour télécharger",
                    data=f,
                    file_name="apitrack_backup.db",
                    mime="application/octet-stream"
                )
        st.markdown("#### Restaurer une base existante")
        uploaded_file = st.file_uploader("Choisir un fichier .db", type=["db"])
        if uploaded_file is not None:
            if st.button("⚠️ Restaurer (remplace toutes les données)"):
                with open(DB_PATH, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("Base restaurée ! Rechargez la page.")
                st.rerun()
    
    with tab2:
        st.markdown("#### Supprimer une ruche (et toutes ses données associées)")
        ruche_list = st.session_state.data["ruches"]["ID"].tolist()
        ruche_to_delete = st.selectbox("Choisir la ruche à supprimer", ruche_list)
        if st.button("🗑 Supprimer définitivement", type="primary"):
            delete_ruche(ruche_to_delete)
            st.session_state.data = load_dataframes()
            st.success(f"Ruche {ruche_to_delete} et ses enregistrements supprimés.")
            st.rerun()
    
    with tab3:
        st.markdown("#### Modifier le nom de l'apiculteur")
        new_name = st.text_input("Nom de l'apiculteur", value=st.session_state.apiculteur)
        if st.button("Enregistrer"):
            set_setting("apiculteur", new_name)
            st.session_state.apiculteur = new_name
            st.success("Nom mis à jour")
            st.rerun()
    
    with tab4:
        st.markdown("#### Changer le mot de passe")
        old_pwd = st.text_input("Ancien mot de passe", type="password")
        new_pwd = st.text_input("Nouveau mot de passe", type="password")
        confirm = st.text_input("Confirmer", type="password")
        if st.button("Changer mot de passe"):
            if "username" in st.session_state and verify_login(st.session_state.username, old_pwd):
                if new_pwd == confirm and len(new_pwd) >= 4:
                    change_password(st.session_state.username, new_pwd)
                    st.success("Mot de passe modifié")
                else:
                    st.error("Le nouveau mot de passe doit faire au moins 4 caractères et correspondre.")
            else:
                st.error("Ancien mot de passe incorrect")

# ─────────────────────────────────────────────
# PAGE: CARTE SATELLITE (Zones mellifères)
# ─────────────────────────────────────────────
elif current_page == "carte":
    st.markdown('<div class="page-title">🗺️ Cartographie des zones mellifères</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Placez vos ruches selon la ressource disponible (miel, pollen, gelée royale, propolis)</div>', unsafe_allow_html=True)

    try:
        import folium
        from streamlit_folium import st_folium
    except ImportError:
        st.error("Installez folium et streamlit-folium : pip install folium streamlit-folium")
        st.stop()

    # Centre par défaut : Tlemcen, Algérie
    center = [34.8825, -1.3167]
    m = folium.Map(location=center, zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')

    # Ajouter les zones déjà enregistrées
    zones_df = st.session_state.data["zones"]
    color_map = {"Miel": "#D4820A", "Pollen": "#F59E0B", "Gelée Royale": "#9B59B6", "Propolis": "#22C55E"}
    for _, zone in zones_df.iterrows():
        try:
            lat, lng = map(float, zone['coordonnees'].split(','))
            popup_text = f"<b>{zone['nom']}</b><br>{zone['type_production']}<br>{zone['flore']}"
            folium.Marker(
                [lat, lng],
                popup=popup_text,
                icon=folium.Icon(color=color_map.get(zone['type_production'], "#6B7280"), icon='info-sign')
            ).add_to(m)
        except:
            pass

    # Affichage de la carte
    st.subheader("Cliquez sur la carte pour ajouter une zone")
    output = st_folium(m, width=700, height=500)

    if output and output.get('last_clicked'):
        lat = output['last_clicked']['lat']
        lng = output['last_clicked']['lng']
        st.session_state['temp_lat'] = lat
        st.session_state['temp_lng'] = lng
        st.success(f"Position sélectionnée : {lat:.5f}, {lng:.5f}")

    # Formulaire d'ajout
    with st.form("add_zone_form"):
        st.markdown("### Ajouter une nouvelle zone")
        nom = st.text_input("Nom de la zone (ex: Plaine du Romarin)")
        type_prod = st.selectbox("Type de production", ["Miel", "Pollen", "Gelée Royale", "Propolis"])
        flore = st.text_input("Flore mellifère dominante (ex: Romarin, Jujubier, Eucalyptus...)")
        coords = f"{st.session_state.get('temp_lat', '')},{st.session_state.get('temp_lng', '')}"
        st.caption(f"Coordonnées : {coords if coords != ',' else 'Cliquez d'abord sur la carte'}")
        submitted = st.form_submit_button("Enregistrer la zone")
        if submitted:
            if not nom or not flore or coords == ",":
                st.error("Veuillez remplir tous les champs et cliquer sur la carte.")
            else:
                new_zone = {
                    "nom": nom,
                    "type_production": type_prod,
                    "flore": flore,
                    "coordonnees": coords,
                    "date_creation": datetime.now().strftime("%Y-%m-%d")
                }
                add_zone(new_zone)
                st.session_state.data = load_dataframes()
                st.success(f"Zone '{nom}' ajoutée !")
                st.rerun()

    # Afficher les zones existantes sous forme de tableau
    st.subheader("Zones enregistrées")
    if not zones_df.empty:
        st.dataframe(zones_df[["nom", "type_production", "flore", "coordonnees", "date_creation"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("Aucune zone enregistrée. Utilisez la carte ci-dessus pour en ajouter.")

# ─────────────────────────────────────────────
# PAGE: DASHBOARD (inchangée)
# ─────────────────────────────────────────────
elif current_page == "dashboard":
    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]

    st.markdown('<div class="page-title">🐝 Vue d\'ensemble — ApiTrack Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Tableau de bord centralisé · Saison 2024–2025</div>', unsafe_allow_html=True)

    total_miel = df["Miel_kg"].sum()
    total_pollen = df["Pollen_kg"].sum()
    total_gelee_g = df["gelee_g"].sum()
    ca_miel = (rec[rec["Type"]=="Miel"]["Quantite_kg"] * rec[rec["Type"]=="Miel"]["Prix_kg"]).sum()
    ca_pollen = (rec[rec["Type"]=="Pollen"]["Quantite_kg"] * rec[rec["Type"]=="Pollen"]["Prix_kg"]).sum()
    ca_gelee = (rec[rec["Type"]=="Gelée Royale"]["Quantite_kg"] * rec[rec["Type"]=="Gelée Royale"]["Prix_kg"]).sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(metric_card("🏠", str(len(df)), "Ruches actives", "+2 ce mois"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("🍯", f"{total_miel:.0f} kg", "Miel récolté", "+18% vs 2023"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🌼", f"{total_pollen:.1f} kg", "Pollen récolté", "+22% vs 2023"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("👑", f"{total_gelee_g:.0f} g", "Gelée royale", "+35% vs 2023"), unsafe_allow_html=True)
    with c5:
        ca_total = ca_miel + ca_pollen + ca_gelee
        st.markdown(metric_card("💰", f"{ca_total:,.0f} DA", "Chiffre d'affaires", "+25% vs 2023"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        section_header("📊 Production par type (2024)")
        rec_df = rec.copy()
        rec_df["Valeur"] = rec_df.apply(lambda r: r["Quantite_kg"]*r["Prix_kg"], axis=1)
        prod_by_type = rec_df.groupby("Type").agg({"Quantite_kg":"sum","Valeur":"sum"}).reset_index()

        fig = go.Figure()
        colors = {"Miel": "#D4820A", "Pollen": "#F59E0B", "Gelée Royale": "#9B59B6"}
        for _, row in prod_by_type.iterrows():
            fig.add_trace(go.Bar(
                x=[row["Type"]], y=[row["Valeur"]],
                name=row["Type"],
                marker_color=colors.get(row["Type"], "#6B7280"),
                text=f"{row['Valeur']:,.0f} DA",
                textposition="outside",
                textfont=dict(size=12, color="#4A3728"),
            ))
        fig.update_layout(
            height=280, showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            yaxis=dict(showgrid=True, gridcolor='rgba(180,150,80,0.15)', tickfont=dict(color='#6B6040')),
            xaxis=dict(tickfont=dict(size=13, color='#4A3728', family='Playfair Display')),
            margin=dict(l=10, r=10, t=30, b=10),
            bargap=0.35
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        section_header("📈 Évolution mensuelle de la production")
        months = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
        miel_m = [0,8,12,35,60,75,55,40,22,5,0,0]
        pollen_m = [0,5,18,28,22,15,10,8,5,2,0,0]
        gelee_m = [0,0,8,18,35,48,38,25,12,0,0,0]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=months, y=miel_m, name="Miel (kg)", fill='tozeroy',
            fillcolor='rgba(212,130,10,0.12)', line=dict(color='#D4820A', width=2.5),
            mode='lines+markers', marker=dict(size=6, color='#D4820A')))
        fig2.add_trace(go.Scatter(x=months, y=pollen_m, name="Pollen (kg)", fill='tozeroy',
            fillcolor='rgba(245,158,11,0.1)', line=dict(color='#F59E0B', width=2, dash='dot'),
            mode='lines+markers', marker=dict(size=5, color='#F59E0B')))
        fig2.add_trace(go.Scatter(x=months, y=[g*10 for g in gelee_m], name="Gelée royale (g×10)", fill='tozeroy',
            fillcolor='rgba(155,89,182,0.1)', line=dict(color='#9B59B6', width=2, dash='dash'),
            mode='lines+markers', marker=dict(size=5, color='#9B59B6')))
        fig2.update_layout(
            height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=11, color='#4A3728'), bgcolor='rgba(255,255,255,0.8)'),
            xaxis=dict(tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
            yaxis=dict(tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with col_r:
        section_header("🚨 Alertes prioritaires")
        alertes = [
            ("🔴", "CRITIQUE — B-07 : Varroa >3.8%. Traitement en cours, réévaluation requise sous 7 jours.", "alert-danger"),
            ("🔴", "CRITIQUE — C-05 : Absence de reine suspectée. Inspection urgente nécessaire.", "alert-danger"),
            ("🟠", "ATTENTION — A-08 : Varroa 2.1%, surveiller l'évolution.", "alert-warning"),
            ("✅", "BIEN — D-02 : Colonie très forte (10 cadres). Essaimage probable dans 10–14 jours.", "alert-success"),
            ("👑", "INFO — C-12 : Récolte de gelée royale programmée dans 3 jours.", "alert-royal"),
        ]
        for icon, txt, cls in alertes:
            st.markdown(alert(icon, txt, cls), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("🌤️ Conditions du rucher")
        st.markdown("""
        <div style="background:linear-gradient(135deg,#2D4A1E,#3D6B2C);border-radius:16px;padding:22px;color:white">
            <div style="font-size:10px;opacity:0.6;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px">Aujourd'hui — Tlemcen</div>
            <div style="font-family:'Playfair Display',serif;font-size:44px;font-weight:700;line-height:1">22°C</div>
            <div style="font-size:14px;opacity:0.85;margin-top:4px">☀️ Ensoleillé — Excellent pour la miellée</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:18px;
                        padding-top:16px;border-top:1px solid rgba(255,255,255,0.15)">
                <div style="text-align:center">
                    <div style="font-size:18px;font-weight:600">65%</div>
                    <div style="font-size:10px;opacity:0.55;text-transform:uppercase;letter-spacing:0.06em">Humidité</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:18px;font-weight:600">12 km/h</div>
                    <div style="font-size:10px;opacity:0.55;text-transform:uppercase;letter-spacing:0.06em">Vent</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:18px;font-weight:600">8/10</div>
                    <div style="font-size:10px;opacity:0.55;text-transform:uppercase;letter-spacing:0.06em">Indice miellée</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("🥧 Répartition du CA par produit")
        fig_pie = go.Figure(go.Pie(
            labels=["🍯 Miel", "🌼 Pollen", "👑 Gelée Royale"],
            values=[ca_miel, ca_pollen, ca_gelee],
            hole=0.55,
            marker=dict(colors=["#D4820A","#F59E0B","#9B59B6"],
                        line=dict(color='white', width=3)),
            textfont=dict(size=12, color='#4A3728'),
            hovertemplate="%{label}: %{value:,.0f} DA<extra></extra>"
        ))
        fig_pie.update_layout(
            height=240, paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(font=dict(size=11, color='#4A3728'), bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=0, r=0, t=10, b=10),
            annotations=[dict(text=f"{ca_total:,.0f}<br>DA", x=0.5, y=0.5,
                              font=dict(size=13, color='#4A3728', family='Playfair Display'), showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🏠 Aperçu des ruches", "Statut en temps réel · Double-clic pour détails")
    cols = st.columns(4)
    for i, (_, r) in enumerate(df.iterrows()):
        with cols[i % 4]:
            st.markdown(ruche_card_html(r), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: RUCHES (inchangée, mais adaptée à 'gelee_g')
# ─────────────────────────────────────────────
elif current_page == "ruches":
    st.markdown('<div class="page-title">🏠 Gestion des Ruches</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Inventaire complet · Profils de production · Santé des colonies</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🃏 Cartes ruches", "📋 Tableau détaillé", "📊 Analyses comparatives", "➕ Nouvelle ruche"])

    with tab1:
        df = st.session_state.data["ruches"]
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            f_statut = st.selectbox("Filtrer par statut", ["Tous","Excellent","Bon","Attention","Critique"])
        with col_filter2:
            f_profil = st.selectbox("Filtrer par profil", ["Tous","Miel","Pollen","Gelée Royale","Résistance"])
        with col_filter3:
            f_race = st.selectbox("Filtrer par race", ["Toutes"] + list(df["Race"].unique()))

        filtered = df.copy()
        if f_statut != "Tous": filtered = filtered[filtered["Statut"] == f_statut]
        if f_profil != "Tous": filtered = filtered[filtered["Profil_prod"] == f_profil]
        if f_race != "Toutes": filtered = filtered[filtered["Race"] == f_race]

        cols = st.columns(4)
        for i, (_, r) in enumerate(filtered.iterrows()):
            with cols[i % 4]:
                st.markdown(ruche_card_html(r), unsafe_allow_html=True)
                if st.button("Voir détails", key=f"btn_ruche_{r['ID']}"):
                    st.session_state["selected_ruche"] = r["ID"]

        if "selected_ruche" in st.session_state:
            rid = st.session_state["selected_ruche"]
            row = df[df["ID"]==rid].iloc[0]
            st.markdown("---")
            st.markdown(f'<div class="section-header">🔍 Détail — {row["Nom"]} ({rid})</div>', unsafe_allow_html=True)
            dc1, dc2 = st.columns([2, 1])
            with dc1:
                st.markdown(f"""
                <div class="morph-card">
                    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px">
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">Race</div>
                             <div style="font-weight:600;margin-top:3px">{row['Race']}</div></div>
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">Site</div>
                             <div style="font-weight:600;margin-top:3px">{row['Site']}</div></div>
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">Reine</div>
                             <div style="font-weight:600;margin-top:3px;font-family:JetBrains Mono,monospace;font-size:12px">{row['Reine_id']}</div></div>
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">Création</div>
                             <div style="font-weight:600;margin-top:3px">{row['Date_creation']}</div></div>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">🍯 Miel</div>
                             <div style="font-weight:700;font-size:18px;color:#D4820A;margin-top:3px">{row['Miel_kg']} kg</div></div>
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">🌼 Pollen</div>
                             <div style="font-weight:700;font-size:18px;color:#F59E0B;margin-top:3px">{row['Pollen_kg']} kg</div></div>
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">👑 Gelée R.</div>
                             <div style="font-weight:700;font-size:18px;color:#9B59B6;margin-top:3px">{row['gelee_g']} g</div></div>
                        <div><div style="font-size:11px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">🛡️ VSH</div>
                             <div style="font-weight:700;font-size:18px;color:#22C55E;margin-top:3px">{row['VSH_pct']}%</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with dc2:
                st.plotly_chart(production_radar(row), use_container_width=True, config={"displayModeBar":False})

    with tab2:
        df = st.session_state.data["ruches"]
        display_cols = ["ID","Nom","Race","Site","Statut","Profil_prod","Poids_kg","Varroa_pct","Miel_kg","Pollen_kg","gelee_g","VSH_pct"]
        st.dataframe(
            df[display_cols].rename(columns={"Profil_prod":"Profil","Varroa_pct":"Varroa %",
                "Miel_kg":"Miel (kg)","Pollen_kg":"Pollen (kg)","gelee_g":"Gelée (g)","VSH_pct":"VSH %"}),
            use_container_width=True, hide_index=True,
            column_config={
                "Statut": st.column_config.SelectboxColumn(options=["Excellent","Bon","Attention","Critique"]),
                "Varroa %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=5),
                "Miel (kg)": st.column_config.NumberColumn(format="%.1f kg"),
                "VSH %": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
            }
        )
        st.markdown("#### Supprimer une ruche")
        del_id = st.selectbox("Choisir l'ID de la ruche à supprimer", df["ID"].tolist())
        if st.button("🗑 Supprimer cette ruche", type="primary"):
            delete_ruche(del_id)
            st.session_state.data = load_dataframes()
            st.success(f"Ruche {del_id} supprimée.")
            st.rerun()

    with tab3:
        df = st.session_state.data["ruches"]
        section_header("📊 Comparaison des productions")

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=df["ID"], y=df["Miel_kg"], name="🍯 Miel (kg)",
            marker_color='#D4820A', text=df["Miel_kg"], textposition='outside'))
        fig_comp.add_trace(go.Bar(x=df["ID"], y=df["Pollen_kg"]*5, name="🌼 Pollen (kg×5)",
            marker_color='#F59E0B', text=df["Pollen_kg"], textposition='outside'))
        fig_comp.add_trace(go.Bar(x=df["ID"], y=df["gelee_g"]/10, name="👑 Gelée (g/10)",
            marker_color='#9B59B6', text=df["gelee_g"].astype(str)+"g", textposition='outside'))
        fig_comp.update_layout(
            barmode='group', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            xaxis=dict(tickfont=dict(color='#4A3728'), gridcolor='rgba(180,150,80,0.1)'),
            yaxis=dict(tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)', title="Quantité normalisée"),
            legend=dict(font=dict(size=11), bgcolor='rgba(255,255,255,0.8)'),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar":False})

        section_header("🎯 Score global par ruche")
        df["Score"] = (df["Miel_kg"]/20*25 + df["Pollen_kg"]/5*15 + df["gelee_g"]/200*15 +
                       df["VSH_pct"]/100*25 + df["Douceur"]/100*10 + df["Economie_hiv"]/100*10).clip(0,100)
        fig_score = go.Figure(go.Bar(
            x=df["Score"].round(1), y=df["Nom"], orientation='h',
            marker=dict(color=df["Score"],colorscale=[[0,'#fee2e2'],[0.5,'#fef9c3'],[1,'#dcfce7']],
                        line=dict(color='white',width=1)),
            text=[f"{s:.0f}/100" for s in df["Score"]], textposition='inside',
            textfont=dict(color='#1E1A0F', size=12, family='JetBrains Mono')
        ))
        fig_score.update_layout(
            height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            xaxis=dict(range=[0,105], tickfont=dict(color='#6B6040')),
            yaxis=dict(tickfont=dict(color='#4A3728', size=12)),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_score, use_container_width=True, config={"displayModeBar":False})

    with tab4:
        st.markdown('<div class="section-header">Enregistrer une nouvelle ruche</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nid = st.text_input("Identifiant ruche *", placeholder="Ex : E-01")
            nnom = st.text_input("Nom de la ruche *", placeholder="Ex : La Dorée")
            nrace = st.selectbox("Race (sous-espèce)", ["A. m. intermissa","A. m. sahariensis","A. m. ligustica","A. m. carnica","Hybride","Indéterminée"])
            nsite = st.text_input("Site / Rucher", placeholder="Ex : Verger du Cèdre")
            nprofil = st.selectbox("Profil de production", ["Miel","Pollen","Gelée Royale","Résistance"])
        with c2:
            ndate = st.date_input("Date de création", value=datetime.now())
            ntype = st.selectbox("Type de ruche", ["Dadant 10 cadres","Langstroth","Warré","Top-bar","Traditionnel"])
            npoids = st.number_input("Poids initial (kg)", min_value=0.0, value=18.0, step=0.5)
            nstatut = st.selectbox("Statut initial", ["Excellent","Bon","Attention","Critique"])
            nreine = st.text_input("ID Reine", placeholder="Ex : R-2025-01")
        nnotes = st.text_area("Observations initiales", placeholder="Notes sur la colonie, l'environnement…")

        if st.button("✓ Enregistrer la ruche", type="primary"):
            if not nid or not nnom:
                st.error("Renseignez l'identifiant et le nom.")
            elif nid in st.session_state.data["ruches"]["ID"].values:
                st.error(f"L'ID {nid} existe déjà.")
            else:
                new_row = {
                    "ID": nid,
                    "Nom": nnom,
                    "Race": nrace,
                    "Site": nsite,
                    "Poids_kg": npoids,
                    "Varroa_pct": 0.0,
                    "Miel_kg": 0,
                    "Pollen_kg": 0,
                    "gelee_g": 0,
                    "Statut": nstatut,
                    "Reine_id": nreine if nreine else "À définir",
                    "VSH_pct": 70,
                    "Douceur": 80,
                    "Economie_hiv": 75,
                    "Essaimage_pct": 30,
                    "Date_creation": str(ndate),
                    "Cadres_couverts": 0,
                    "Cadres_couvain": 0,
                    "Temp_int": 35.0,
                    "Profil_prod": nprofil,
                    "Glossa_mm": 6.0,
                    "L_aile_mm": 9.2,
                    "Ri": 2.5,
                    "Tomentum_pct": 35,
                    "Pigment_scutellum": 5,
                    "Ti_L_mm": 3.0
                }
                add_ruche(new_row)
                st.session_state.data = load_dataframes()
                st.success(f"✅ Ruche {nid} « {nnom} » enregistrée avec succès !")
                st.balloons()

# ─────────────────────────────────────────────
# PAGE: INSPECTIONS (inchangée)
# ─────────────────────────────────────────────
elif current_page == "inspections":
    st.markdown('<div class="page-title">🔍 Inspections</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Journal de terrain · Suivi sanitaire · Historique complet</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 Nouvelle inspection", "📅 Historique"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            ruche_ids = st.session_state.data["ruches"]["ID"].tolist()
            ruche_noms = [f"{r['ID']} — {r['Nom']}" for _, r in st.session_state.data["ruches"].iterrows()]
            insp_ruche = st.selectbox("Ruche inspectée *", ruche_noms)
            insp_date = st.date_input("Date d'inspection *", value=datetime.now())
            insp_poids = st.number_input("Poids pesée (kg)", min_value=0.0, value=20.0, step=0.1)
            insp_temp = st.number_input("Température intérieure (°C)", min_value=0.0, value=35.0, step=0.1)
            insp_cadres = st.slider("Cadres couverts de population", 0, 10, 7)
            insp_couvain = st.slider("Cadres de couvain", 0, 10, 5)
        with c2:
            insp_reine = st.selectbox("Présence reine", ["Observée","Non observée (ponte présente)","Absente"])
            insp_varroa = st.selectbox("Niveau varroa", ["Aucune visible","Faible (<1%)","Modérée (1–3%)","Élevée (>3%)"])
            insp_reserves = st.selectbox("Réserves de miel", ["Excellentes (>15 kg)","Bonnes (8–15 kg)","Faibles (3–8 kg)","Insuffisantes (<3 kg)"])
            insp_comportement = st.selectbox("Comportement", ["Calme","Nerveux","Agressif"])
            insp_maladie = st.multiselect("Signes de maladie", ["Aucun","Loque américaine","Loque européenne","Nosémose","Teigne","Sacbrood"])
            insp_notif = st.selectbox("Statut général", ["Excellent","Bon","Attention","Critique"])
        insp_notes = st.text_area("Observations détaillées", placeholder="Couvain sain, pas de maladie apparente, bonne ponte de la reine…", height=100)

        if st.button("✓ Enregistrer l'inspection", type="primary"):
            new_insp = {
                "Date": str(insp_date),
                "Ruche": insp_ruche.split("—")[0].strip(),
                "Poids_kg": insp_poids,
                "Cadres_couverts": insp_cadres,
                "Varroa": insp_varroa,
                "Reine": insp_reine,
                "Comportement": insp_comportement,
                "Notes": insp_notes
            }
            add_inspection(new_insp)
            st.session_state.data = load_dataframes()
            st.success("✅ Inspection enregistrée avec succès !")

    with tab2:
        df_insp = st.session_state.data["inspections"].sort_values("Date", ascending=False)
        st.markdown('<div class="section-header">📅 Journal chronologique</div>', unsafe_allow_html=True)
        for _, row in df_insp.iterrows():
            varroa_icon = "🔴" if "Élevée" in str(row.get("Varroa","")) else "🟡" if "Modérée" in str(row.get("Varroa","")) else "🟢"
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">{row['Date']} — Ruche {row['Ruche']}</div>
                <div class="timeline-event">{varroa_icon} {row.get('Comportement','—')} · Poids : {row['Poids_kg']} kg</div>
                <div class="timeline-note">{row.get('Notes','—')}</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: TRAITEMENTS (inchangée)
# ─────────────────────────────────────────────
elif current_page == "traitements":
    st.markdown('<div class="page-title">💊 Traitements Vétérinaires</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Conformité réglementaire · Suivi anti-varroa · Historique médicamenteux</div>', unsafe_allow_html=True)

    st.markdown(alert("ℹ️", "Consigner tous les traitements vétérinaires est obligatoire. Les données sont exportables pour conformité réglementaire (Directive EU 2001/82/CE, code algérien de l'apiculture).", "alert-info"), unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["💊 Enregistrer traitement", "📊 Suivi en cours"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            t_ruche = st.selectbox("Ruche(s) traitée(s)", ["Toutes les ruches"] + st.session_state.data["ruches"]["ID"].tolist())
            t_date = st.date_input("Date de début", value=datetime.now())
            t_produit = st.selectbox("Produit utilisé", ["Acide oxalique","Acide formique","Apivar (amitraz)","Apiguard (thymol)","Thymovar","CheckMite+ (coumaphos)","Autre"])
            t_patho = st.selectbox("Pathologie ciblée", ["Varroa destructor","Loque américaine","Loque européenne","Nosémose","Teigne de la cire","Autre"])
        with c2:
            t_dose = st.text_input("Dose appliquée", placeholder="Ex : 5 ml / ruche")
            t_duree = st.number_input("Durée (jours)", min_value=1, value=21)
            t_methode = st.selectbox("Méthode d'application", ["Sublimation","Lanière","Vaporisation","Nourrissement","Autre"])
            t_temp = st.number_input("Température extérieure (°C)", min_value=-10, max_value=50, value=18)
        t_notes = st.text_area("Observations", placeholder="Conditions d'application, état des colonies…")

        if st.button("✓ Enregistrer le traitement", type="primary"):
            new_t = {
                "Date_debut": str(t_date),
                "Ruche": t_ruche,
                "Produit": t_produit,
                "Pathologie": t_patho,
                "Dose": t_dose,
                "Duree_j": t_duree,
                "Statut": "En cours",
                "Progression_pct": 0
            }
            add_traitement(new_t)
            st.session_state.data = load_dataframes()
            st.success("✅ Traitement enregistré !")

    with tab2:
        for _, t in st.session_state.data["traitements"].iterrows():
            color = "#22c55e" if t["Statut"]=="Terminé" else "#ef4444"
            prog = t["Progression_pct"]
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:18px;border:1px solid rgba(180,150,80,0.2);
                        border-left:4px solid {color};margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">
                    <div>
                        <div style="font-weight:600;font-size:14px">{t['Produit']} — {t['Ruche']}</div>
                        <div style="font-size:12px;color:#6B6040;margin-top:3px">{t['Pathologie']} · Débuté le {t['Date_debut']}</div>
                    </div>
                    <span class="badge {'badge-excellent' if t['Statut']=='Terminé' else 'badge-attention'}">{t['Statut']}</span>
                </div>
                <div style="font-size:12px;color:#6B6040;margin-bottom:6px">Progression — {t['Duree_j']} jours</div>
                <div style="height:10px;background:#F5EDD8;border-radius:5px;overflow:hidden">
                    <div style="height:100%;width:{prog}%;background:{'linear-gradient(90deg,#86EFAC,#22C55E)' if prog==100 else 'linear-gradient(90deg,#FB923C,#EF4444)'};border-radius:5px;transition:width 0.5s"></div>
                </div>
                <div style="font-size:11px;color:#6B6040;margin-top:5px">{prog}% complété</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: MIEL (inchangée, mais 'gelee_g' remplace 'Gelée_g')
# ─────────────────────────────────────────────
elif current_page == "miel":
    st.markdown('<div class="page-title">🍯 Production de Miel</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Récoltes · Qualité · Traçabilité · Analyse sensorielle</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]
    miel_rec = rec[rec["Type"]=="Miel"].copy()

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(metric_card("🍯", f"{df['Miel_kg'].sum():.1f} kg", "Total produit"), unsafe_allow_html=True)
    with c2:
        ca = (miel_rec["Quantite_kg"]*miel_rec["Prix_kg"]).sum()
        st.markdown(metric_card("💰", f"{ca:,.0f} DA", "Chiffre d'affaires"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🏆", f"{df['Miel_kg'].max():.1f} kg", "Meilleure ruche"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("📊", f"{df['Miel_kg'].mean():.1f} kg", "Moyenne/ruche"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Analyses", "➕ Enregistrer récolte", "📋 Historique"])

    with tab1:
        c_l, c_r = st.columns(2)
        with c_l:
            section_header("🏆 Production par ruche")
            df_sorted = df.sort_values("Miel_kg", ascending=True)
            fig = go.Figure(go.Bar(
                x=df_sorted["Miel_kg"], y=df_sorted["Nom"], orientation='h',
                marker=dict(color=df_sorted["Miel_kg"], colorscale=[[0,'#FFF8E6'],[1,'#8B5200']],
                            line=dict(color='white',width=1)),
                text=[f"{v:.1f} kg" for v in df_sorted["Miel_kg"]], textposition='inside',
                textfont=dict(color='#4A3728', size=11)
            ))
            fig.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                xaxis=dict(title="kg", tickfont=dict(color='#6B6040')),
                yaxis=dict(tickfont=dict(color='#4A3728', size=12)),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        with c_r:
            section_header("📊 Répartition par type de miel")
            if len(miel_rec) > 0:
                type_grp = miel_rec.groupby("Produit")["Quantite_kg"].sum().reset_index()
                fig2 = go.Figure(go.Pie(
                    labels=type_grp["Produit"], values=type_grp["Quantite_kg"],
                    hole=0.45, marker=dict(colors=["#D4820A","#F5C842","#E8A020","#8B5200","#C4773A"],
                                           line=dict(color='white',width=2)),
                    textfont=dict(size=11),
                    hovertemplate="%{label}: %{value:.1f} kg<extra></extra>"
                ))
                fig2.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)',
                    legend=dict(font=dict(size=10,color='#4A3728'), bgcolor='rgba(0,0,0,0)'),
                    margin=dict(l=0,r=0,t=10,b=10))
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

        section_header("💧 Contrôle qualité — Taux d'humidité")
        st.markdown(alert("ℹ️", "Le taux d'humidité optimal est de 17–18%. Au-delà de 18.5%, risque de fermentation. En dessous de 16%, le miel peut cristalliser prématurément.", "alert-info"), unsafe_allow_html=True)
        if len(miel_rec)>0:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=miel_rec["Produit"], y=miel_rec["Humidite_pct"],
                mode='markers+text', marker=dict(size=14, color=miel_rec["Humidite_pct"],
                colorscale=[[0,'#22c55e'],[0.5,'#f59e0b'],[1,'#ef4444']], cmin=15, cmax=20,
                line=dict(color='white',width=2)), text=[f"{h}%" for h in miel_rec["Humidite_pct"]],
                textposition='top center', textfont=dict(size=11,color='#4A3728')))
            fig3.add_hline(y=18.5, line_dash="dash", line_color="#ef4444", annotation_text="Seuil max (18.5%)")
            fig3.add_hline(y=16.0, line_dash="dash", line_color="#f59e0b", annotation_text="Seuil min (16%)")
            fig3.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                yaxis=dict(range=[14,21], title="Humidité (%)", tickfont=dict(color='#6B6040')),
                xaxis=dict(tickfont=dict(color='#4A3728')),
                margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    with tab2:
        st.markdown('<div class="section-header">Enregistrer une récolte de miel</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            r_date = st.date_input("Date de récolte", value=datetime.now())
            r_ruche = st.selectbox("Ruche", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()])
            r_type = st.selectbox("Type de miel", ["Miel toutes fleurs","Miel de jujubier","Miel de romarin","Miel d'eucalyptus","Miel d'oranger","Miel de thym","Miel de jujubier sauvage"])
            r_qte = st.number_input("Quantité récoltée (kg)", min_value=0.0, value=10.0, step=0.5)
        with c2:
            r_humidite = st.number_input("Humidité (%)", min_value=14.0, max_value=25.0, value=17.5, step=0.1)
            r_couleur = st.selectbox("Couleur (Pfund)", ["Water White (<9)","Extra White (9–17)","White (18–34)","Extra Light Amber (35–50)","Light Amber (51–85)","Amber (86–114)","Dark Amber (>114)"])
            r_prix = st.number_input("Prix de vente (DA/kg)", min_value=0, value=1500, step=100)
            r_certif = st.selectbox("Certification", ["Standard","Bio (certifié)","AOC/IGP","À certifier"])
        r_notes = st.text_area("Notes organoleptiques", placeholder="Arôme, texture, cristallisation, floraison dominante…")
        if st.button("✓ Enregistrer la récolte", type="primary"):
            new_r = {
                "Date": str(r_date),
                "Ruche": r_ruche.split("—")[0].strip(),
                "Type": "Miel",
                "Produit": r_type,
                "Quantite_kg": r_qte,
                "Humidite_pct": r_humidite,
                "Prix_kg": r_prix
            }
            add_recolte(new_r)
            st.session_state.data = load_dataframes()
            st.success(f"✅ Récolte de {r_qte} kg enregistrée !")

    with tab3:
        st.dataframe(miel_rec.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: POLLEN (inchangée)
# ─────────────────────────────────────────────
elif current_page == "pollen":
    st.markdown('<div class="page-title">🌼 Production de Pollen</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Collecte · Séchage · Qualité pollinique · Traçabilité botanique</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]
    pol_rec = rec[rec["Type"]=="Pollen"].copy()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(metric_card("🌼", f"{df['Pollen_kg'].sum():.1f} kg", "Total collecté", "+22% vs 2023"), unsafe_allow_html=True)
    with c2:
        ca_pol = (pol_rec["Quantite_kg"]*pol_rec["Prix_kg"]).sum() if len(pol_rec)>0 else 0
        st.markdown(metric_card("💰", f"{ca_pol:,.0f} DA", "CA Pollen", "+18%"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🏆", f"{df['Pollen_kg'].max():.1f} kg", "Meilleure collectrice"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("🌸", "3", "Espèces dominantes"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(alert("🌼", "<strong>Le pollen frais doit être réfrigéré à 4°C ou congelé immédiatement après collecte.</strong> Séchage conseillé à ≤40°C pendant 24–48h pour préservation des protéines. Humidité cible après séchage : <8%.", "alert-info"), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Analyses", "➕ Enregistrer récolte", "🔬 Palynologie"])

    with tab1:
        c_l, c_r = st.columns(2)
        with c_l:
            section_header("📊 Collecte par ruche (kg)")
            df_pol = df.sort_values("Pollen_kg", ascending=True)
            fig = go.Figure(go.Bar(
                x=df_pol["Pollen_kg"], y=df_pol["Nom"], orientation='h',
                marker_color='#F59E0B',
                text=[f"{v:.1f} kg" for v in df_pol["Pollen_kg"]], textposition='inside',
                textfont=dict(color='#4A3728',size=11)
            ))
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                xaxis=dict(title="kg collecté", tickfont=dict(color='#6B6040')),
                yaxis=dict(tickfont=dict(color='#4A3728',size=12)),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        with c_r:
            section_header("🌸 Répartition des espèces pollinisées")
            especes = ["Romarin","Jujubier","Oranger","Thym","Lavande","Chardon","Alfa","Tournesol"]
            pcts = [28,22,18,12,9,5,4,2]
            colors_esp = ["#F59E0B","#D4820A","#E8A020","#B45309","#92400E","#78350F","#FBBF24","#FCD34D"]
            fig2 = go.Figure(go.Pie(
                labels=especes, values=pcts, hole=0.45,
                marker=dict(colors=colors_esp, line=dict(color='white',width=2)),
                textfont=dict(size=10),
                hovertemplate="%{label}: %{value}%<extra></extra>"
            ))
            fig2.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(size=9,color='#4A3728'), bgcolor='rgba(0,0,0,0)', orientation='v'),
                margin=dict(l=0,r=0,t=10,b=10))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

        section_header("📅 Calendrier de collecte pollinique — Région Oranie")
        mois = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
        pol_m = [0,12,45,80,90,60,35,20,10,5,0,0]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=mois, y=pol_m, fill='tozeroy', name="Intensité collecte",
            fillcolor='rgba(245,158,11,0.2)', line=dict(color='#F59E0B',width=2.5),
            mode='lines+markers', marker=dict(size=7,color='#F59E0B')))
        fig3.update_layout(height=240, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            yaxis=dict(title="Indice de disponibilité",tickfont=dict(color='#6B6040'),gridcolor='rgba(180,150,80,0.1)'),
            xaxis=dict(tickfont=dict(color='#4A3728')),
            margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    with tab2:
        st.markdown('<div class="section-header">Enregistrer une collecte de pollen</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            p_date = st.date_input("Date de collecte", value=datetime.now(), key="p_date")
            p_ruche = st.selectbox("Ruche collectrice", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()], key="p_ruche")
            p_qte = st.number_input("Quantité brute (kg)", min_value=0.0, value=1.5, step=0.1)
            p_qte_sec = st.number_input("Quantité après séchage (kg)", min_value=0.0, value=1.2, step=0.1)
        with c2:
            p_humidite = st.number_input("Humidité après séchage (%)", min_value=4.0, max_value=15.0, value=7.5, step=0.1)
            p_couleur = st.selectbox("Couleur dominante", ["Jaune doré","Orange","Gris-vert","Beige","Brun","Mixte"])
            p_espece = st.text_input("Espèces florales dominantes", placeholder="Ex : Romarin, oranger")
            p_prix = st.number_input("Prix de vente (DA/kg)", min_value=0, value=4500, step=100)
        p_notes = st.text_area("Notes", placeholder="Conditions de collecte, qualité, odeur…", key="p_notes")
        if st.button("✓ Enregistrer la collecte de pollen", type="primary"):
            new_p = {
                "Date": str(p_date),
                "Ruche": p_ruche.split("—")[0].strip(),
                "Type": "Pollen",
                "Produit": f"Pollen — {p_espece if p_espece else 'Mixte'}",
                "Quantite_kg": p_qte_sec,
                "Humidite_pct": p_humidite,
                "Prix_kg": p_prix
            }
            add_recolte(new_p)
            st.session_state.data = load_dataframes()
            st.success(f"✅ Collecte de {p_qte_sec} kg de pollen enregistrée !")

    with tab3:
        section_header("🔬 Analyse palynologique")
        st.markdown(alert("🔬", "<strong>Palynologie apicole :</strong> Identification des grains de pollen sous microscope pour certifier l'origine botanique et géographique du miel. Norme ISO 22000 — Mélissopalynologie (Von der Ohe et al., 2004).", "alert-info"), unsafe_allow_html=True)

        pal_data = {
            "Espèce": ["Ziziphus lotus (Jujubier)","Rosmarinus off. (Romarin)","Citrus sinensis (Oranger)","Lavandula sp. (Lavande)","Thymus vulgaris (Thym)","Eucalyptus glob."],
            "Famille": ["Rhamnaceae","Lamiaceae","Rutaceae","Lamiaceae","Lamiaceae","Myrtaceae"],
            "Taille grain (µm)": ["25–35","15–25","25–35","30–40","18–28","20–30"],
            "Forme": ["Tricolporé","Hexacolpé","Tricolporé","Tricolpé","Hexacolpé","Tricolporé"],
            "Valeur mellifère": ["★★★★★","★★★★","★★★★★","★★★★","★★★★","★★★★"],
            "Période": ["Mai–Juin","Fév–Avr","Avr–Mai","Juin–Jul","Avr–Juin","Nov–Jan"],
        }
        st.dataframe(pd.DataFrame(pal_data), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: GELÉE ROYALE (inchangée, mais 'gelee_g')
# ─────────────────────────────────────────────
elif current_page == "gelee":
    st.markdown('<div class="page-title">👑 Gelée Royale</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Production · Qualité · Conservation · Commercialisation</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]
    gr_rec = rec[rec["Type"]=="Gelée Royale"].copy()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(metric_card("👑", f"{df['gelee_g'].sum()} g", "Total produit (2024)", "+35% vs 2023"), unsafe_allow_html=True)
    with c2:
        ca_gr = (gr_rec["Quantite_kg"]*gr_rec["Prix_kg"]).sum() if len(gr_rec)>0 else 0
        st.markdown(metric_card("💰", f"{ca_gr:,.0f} DA", "CA Gelée Royale"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("🏆", f"{df['gelee_g'].max()} g", "Meilleure productrice"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("🔬", "3", "Ruches productrices"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(alert("👑", """<strong>Conservation de la gelée royale :</strong> 
        La gelée royale fraîche doit être conservée à <strong>−18°C (congélation)</strong> ou à <strong>4°C pendant max 6 mois</strong>. 
        Ne jamais conserver à température ambiante. Le pH optimal est de 3.5–4.5. 
        Teneur en 10-HDA (acide 10-hydroxy-2-décénoïque) : indicateur de qualité — minimum 1.4% selon la norme européenne.""", "alert-royal"), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Analyses", "➕ Enregistrer récolte", "🔬 Contrôle qualité"])

    with tab1:
        c_l, c_r = st.columns(2)
        with c_l:
            section_header("📊 Production par ruche (g)")
            df_gr = df[df["gelee_g"]>0].sort_values("gelee_g", ascending=True)
            fig = go.Figure(go.Bar(
                x=df_gr["gelee_g"], y=df_gr["Nom"], orientation='h',
                marker_color='#9B59B6',
                text=[f"{v} g" for v in df_gr["gelee_g"]], textposition='inside',
                textfont=dict(color='white',size=11)
            ))
            fig.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(250,245,255,0.5)',
                xaxis=dict(title="grammes", tickfont=dict(color='#6B6040')),
                yaxis=dict(tickfont=dict(color='#4A3728',size=12)),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        with c_r:
            section_header("📅 Calendrier de production GR")
            mois = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
            gr_m = [0,0,15,45,80,95,75,50,20,5,0,0]
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=mois, y=gr_m, fill='tozeroy',
                fillcolor='rgba(155,89,182,0.15)', line=dict(color='#9B59B6',width=2.5),
                mode='lines+markers', marker=dict(size=7,color='#9B59B6')))
            fig2.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(250,245,255,0.5)',
                yaxis=dict(title="Indice de production",tickfont=dict(color='#6B6040'),gridcolor='rgba(155,89,182,0.1)'),
                xaxis=dict(tickfont=dict(color='#4A3728')),
                margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

        section_header("🔬 Composition chimique typique")
        comp_data = {
            "Composant": ["Eau","Protéines totales","Glucides","Acide 10-HDA","Lipides","Minéraux","Acétylcholine"],
            "Teneur typique": ["67–70%","11–14%","10–16%","1.4–2.4%","3–7%","0.8–1.5%","0.1–0.3 mg/g"],
            "Rôle / intérêt": ["Activité biologique","Royalactine, gellines","Énergie","Marqueur qualité","Acides gras rares","Oligoéléments","Activité physiologique"],
            "Norme qualité": ["<72%",">11%",">10%",">1.4%","—","—","—"],
        }
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

    with tab2:
        st.markdown('<div class="section-header">Enregistrer une récolte de gelée royale</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            gr_date = st.date_input("Date de récolte", value=datetime.now(), key="gr_date")
            gr_ruche = st.selectbox("Ruche productrice", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()], key="gr_ruche")
            gr_qte_g = st.number_input("Quantité récoltée (g)", min_value=0.0, value=50.0, step=1.0)
            gr_nb_cellules = st.number_input("Nombre de cellules royales", min_value=0, value=30, step=1)
        with c2:
            gr_hda = st.number_input("Taux 10-HDA mesuré (%)", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
            gr_ph = st.number_input("pH mesuré", min_value=3.0, max_value=6.0, value=3.8, step=0.1)
            gr_conservation = st.selectbox("Méthode de conservation", ["Congélation (−18°C)","Réfrigération (4°C)","Lyophilisation","Mélange au miel"])
            gr_prix = st.number_input("Prix de vente (DA/g)", min_value=0, value=120, step=10)
        gr_notes = st.text_area("Observations", placeholder="Couleur, consistance, odeur, conditions de récolte…", key="gr_notes")
        if st.button("✓ Enregistrer la récolte de gelée royale", type="primary"):
            new_gr = {
                "Date": str(gr_date),
                "Ruche": gr_ruche.split("—")[0].strip(),
                "Type": "Gelée Royale",
                "Produit": "Gelée royale fraîche",
                "Quantite_kg": gr_qte_g/1000,
                "Humidite_pct": 68.0,
                "Prix_kg": gr_prix*1000
            }
            add_recolte(new_gr)
            st.session_state.data = load_dataframes()
            hda_ok = gr_hda >= 1.4
            ph_ok = 3.5 <= gr_ph <= 4.5
            if hda_ok and ph_ok:
                st.success(f"✅ Récolte de {gr_qte_g}g de gelée royale enregistrée ! Qualité conforme (10-HDA: {gr_hda}%, pH: {gr_ph})")
            else:
                st.warning(f"⚠️ Récolte enregistrée mais attention : {'10-HDA < 1.4% (sous norme)' if not hda_ok else ''} {'pH hors norme' if not ph_ok else ''}")

    with tab3:
        section_header("🔬 Contrôle qualité & normes")
        st.markdown(alert("📋", """<strong>Normes de qualité de la gelée royale (selon Codex Alimentarius CAC/RCP 82-2013) :</strong><br>
        • Humidité : 60–70% | • Protéines totales : ≥11% | • Acide 10-HDA : ≥1.4% (norme européenne : ≥1.6%)
        | • pH : 3.5–4.5 | • Sucres réducteurs : ≤15% | • Absence de contamination par antibiotiques""", "alert-info"), unsafe_allow_html=True)

        if len(gr_rec) > 0:
            st.dataframe(gr_rec[["Date","Ruche","Produit","Quantite_kg","Humidite_pct"]].rename(
                columns={"Quantite_kg":"Quantité (kg)","Humidite_pct":"Humidité (%)"}),
                use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: MORPHOMÉTRIE (inchangée)
# ─────────────────────────────────────────────
elif current_page == "morphometrie":
    st.markdown('<div class="page-title">🔬 Morphométrie des Abeilles</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Caractérisation morphologique selon Ruttner (1988) · Analyse discriminante · Classification raciale</div>', unsafe_allow_html=True)

    st.markdown(alert("🔬", """<strong>Protocole morphométrique</strong> basé sur Ruttner (1988), Cornuet & Fresnaye (1989), 
        Kandemir et al. (2011) et Baylac et al. (2008). 
        36 caractères mesurables : aile antérieure, aile postérieure, corps, patte. 
        Classification par analyse discriminante.""", "alert-info"), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📷 Saisie mesures", "📐 Référentiel", "📊 Analyses comparatives", "📋 Historique"])

    with tab1:
        st.markdown('<div class="section-header">Saisie des mesures morphométriques</div>', unsafe_allow_html=True)
        c_form, c_result = st.columns([3, 2])

        with c_form:
            m_ruche = st.selectbox("Ruche analysée", [f"{r['ID']} — {r['Nom']}" for _,r in st.session_state.data["ruches"].iterrows()])
            m_date = st.date_input("Date d'analyse", value=datetime.now(), key="m_date")
            m_analyste = st.text_input("Analyste", value="Mohammed A.")
            m_n_abeilles = st.number_input("Nombre d'abeilles mesurées", min_value=1, value=10, step=1)

            st.markdown("**📏 Mesures de l'aile antérieure**")
            col1, col2, col3 = st.columns(3)
            with col1: m_L = st.number_input("Longueur L (mm)", min_value=7.0, max_value=12.0, value=9.18, step=0.01, format="%.2f")
            with col2: m_B = st.number_input("Largeur B (mm)", min_value=2.5, max_value=4.5, value=3.21, step=0.01, format="%.2f")
            with col3: m_Ri = st.number_input("Indice cubital Ri", min_value=1.0, max_value=5.0, value=2.45, step=0.01, format="%.2f")
            col4, col5 = st.columns(2)
            with col4: m_DI3 = st.number_input("Cellule 3 DI3 (mm)", min_value=1.0, max_value=2.5, value=1.72, step=0.01, format="%.2f")
            with col5: m_OI = st.selectbox("Indice discoïdal (OI)", ["+ (positif)","- (négatif)"])

            st.markdown("**📐 Angles alaires**")
            col6, col7 = st.columns(2)
            with col6: m_A4 = st.number_input("Angle A4 (°)", min_value=85.0, max_value=115.0, value=99.2, step=0.1, format="%.1f")
            with col7: m_B4 = st.number_input("Angle B4 (°)", min_value=80.0, max_value=110.0, value=91.5, step=0.1, format="%.1f")

            st.markdown("**🦵 Mesures de la patte postérieure**")
            col8, col9, col10 = st.columns(3)
            with col8: m_Ti = st.number_input("Tibia Ti-L (mm)", min_value=2.0, max_value=4.0, value=3.01, step=0.01, format="%.2f")
            with col9: m_Ba = st.number_input("Basitarse Ba-L (mm)", min_value=1.2, max_value=2.5, value=1.88, step=0.01, format="%.2f")
            with col10: m_BaW = st.number_input("Larg. basitarse (mm)", min_value=0.7, max_value=1.5, value=1.09, step=0.01, format="%.2f")

            st.markdown("**🫀 Mesures abdominales**")
            col11, col12 = st.columns(2)
            with col11: m_T3 = st.number_input("Tergite 3 T3-L (mm)", min_value=3.5, max_value=5.5, value=4.78, step=0.01, format="%.2f")
            with col12: m_Tom = st.number_input("Tomentum T4 (%)", min_value=0, max_value=100, value=37, step=1)

            st.markdown("**👅 Langue & pigmentation**")
            col13, col14 = st.columns(2)
            with col13: m_Ac = st.number_input("Glossa / langue Ac (mm)", min_value=5.0, max_value=8.0, value=6.12, step=0.01, format="%.2f")
            with col14: m_Pv = st.slider("Pigmentation scutellum (1–9)", 1, 9, 5)

            m_notes = st.text_area("Observations", placeholder="Qualité de l'image, conditions, remarques…", key="m_notes")

        with c_result:
            st.markdown('<div class="section-header">🧬 Résultat de classification</div>', unsafe_allow_html=True)

            def classify_bee(L, Ri, Ac, m_Pv, m_Tom, Ti):
                scores = {
                    "A. m. intermissa": 0,
                    "A. m. sahariensis": 0,
                    "A. m. ligustica": 0,
                    "A. m. carnica": 0,
                    "Hybride": 0,
                }
                if 8.9<=L<=9.6: scores["A. m. intermissa"]+=20
                if 8.7<=L<=9.3: scores["A. m. sahariensis"]+=20
                if 9.1<=L<=9.8: scores["A. m. ligustica"]+=15; scores["A. m. carnica"]+=15
                if 2.0<=Ri<=2.8: scores["A. m. intermissa"]+=20
                if 2.1<=Ri<=2.9: scores["A. m. sahariensis"]+=18
                if 2.4<=Ri<=3.2: scores["A. m. ligustica"]+=20
                if 2.6<=Ri<=3.5: scores["A. m. carnica"]+=20
                if 5.9<=Ac<=6.3: scores["A. m. intermissa"]+=25
                if 5.8<=Ac<=6.2: scores["A. m. sahariensis"]+=20
                if 6.3<=Ac<=6.7: scores["A. m. ligustica"]+=25
                if 6.4<=Ac<=6.8: scores["A. m. carnica"]+=25
                if 4<=m_Pv<=7: scores["A. m. intermissa"]+=15
                if 5<=m_Pv<=8: scores["A. m. sahariensis"]+=15
                if 1<=m_Pv<=3: scores["A. m. ligustica"]+=15; scores["A. m. carnica"]+=15
                if 30<=m_Tom<=45: scores["A. m. intermissa"]+=20
                if 25<=m_Tom<=40: scores["A. m. sahariensis"]+=15
                if 45<=m_Tom<=60: scores["A. m. ligustica"]+=20
                if 35<=m_Tom<=50: scores["A. m. carnica"]+=15

                total = sum(scores.values())
                probs = {k: v/total*100 for k, v in scores.items()}
                best = max(probs, key=probs.get)
                if probs[best] < 40: best = "Hybride"
                return best, probs

            best_race, probs = classify_bee(m_L, m_Ri, m_Ac, m_Pv, m_Tom, m_Ti)
            conf = probs[best_race]
            race_badge_cls = RACE_BADGES.get(best_race, "badge-hybride")

            st.markdown(f"""
            <div class="race-result-box">
                <div style="font-size:11px;color:#6B6040;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em">Taxon identifié</div>
                <div class="race-name">{best_race}</div>
                <div style="margin-top:8px"><span class="race-conf">Confiance : {conf:.0f}%</span></div>
            </div>
            """, unsafe_allow_html=True)

            for race, pct in sorted(probs.items(), key=lambda x: -x[1]):
                st.markdown(f"""
                <div style="margin-bottom:8px">
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
                        <span style="color:#4A3728;font-weight:500">{race}</span>
                        <span style="font-family:'JetBrains Mono',monospace;color:#6B6040">{pct:.0f}%</span>
                    </div>
                    <div style="height:8px;background:#F5EDD8;border-radius:4px;overflow:hidden">
                        <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#F5C842,#D4820A);border-radius:4px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#F0FDF4;border-radius:12px;padding:14px;border:1px solid #BBF7D0;font-size:12px;line-height:1.7;color:#166534">
                <strong>Interprétation :</strong> L'analyse de {m_n_abeilles} individus classe cette colonie comme 
                <strong>{best_race}</strong> avec une confiance de <strong>{conf:.0f}%</strong>. 
                Indice cubital Ri={m_Ri:.2f}, glossa={m_Ac:.2f}mm, tomentum={m_Tom}%.
                Référence : <em>Ruttner (1988), Chahbar et al. (2013)</em>.
            </div>
            """, unsafe_allow_html=True)

        if st.button("💾 Sauvegarder l'analyse morphométrique", type="primary"):
            new_m = {
                "Date": str(m_date),
                "Ruche": m_ruche.split("—")[0].strip(),
                "Taxon": best_race,
                "Confiance_pct": round(conf,0),
                "L_aile_mm": m_L,
                "Ri": m_Ri,
                "Glossa_mm": m_Ac,
                "B_aile_mm": m_B,
                "DI3_mm": m_DI3,
                "A4_deg": m_A4,
                "B4_deg": m_B4,
                "Ti_L_mm": m_Ti,
                "T3_L_mm": m_T3,
                "Tomentum_pct": m_Tom,
                "Pigment": m_Pv,
                "OI": m_OI.split()[0],
                "Analyste": m_analyste
            }
            add_morph_analyse(new_m)
            st.session_state.data = load_dataframes()
            st.success(f"✅ Analyse sauvegardée : {best_race} ({conf:.0f}% confiance)")

    with tab2:
        section_header("📐 Caractères morphométriques de référence (Ruttner 1988 / Kandemir 2011)")
        ref_data = {
            "Code": ["L","B","Ri","DI3","OI","T3-L","T4-L","T4-W","S4-L","Fe-L","Ti-L","Ba-L","Ba-W","Ac","Co1","Co2","Pv","Hb"],
            "Caractère": ["Longueur aile ant.","Largeur aile ant.","Indice cubital (a/b)","Longueur cellule 3",
                "Indice discoïdal","Largeur tergite 3","Largeur tergite 4","Tomentum tergite 4","Longueur sternite 4",
                "Longueur fémur P3","Longueur tibia P3","Longueur basitarse","Largeur basitarse","Glossa / langue",
                "Angle A4","Angle B4","Pigmentation scutellum","Pubescence abd. 4"],
            "Unité": ["mm","mm","ratio","mm","ratio","mm","mm","%","mm","mm","mm","mm","mm","mm","°","°","score 1–9","mm"],
            "A.m. intermissa": ["8.9–9.6","3.0–3.4","2.0–2.8","1.5–1.9","+/−","4.6–5.0","4.5–4.9","30–45","2.5–2.9","2.6–2.9","2.8–3.2","1.7–2.0","1.0–1.2","5.9–6.3","96–103","88–95","4–7","0.3–0.5"],
            "A.m. ligustica": ["9.1–9.8","3.1–3.5","2.4–3.2","1.6–2.0","+","4.7–5.1","4.7–5.1","45–60","2.6–3.0","2.7–3.0","2.9–3.3","1.8–2.1","1.0–1.2","6.3–6.7","98–105","89–97","1–3","0.2–0.4"],
            "A.m. carnica": ["9.1–9.8","3.1–3.4","2.6–3.5","1.6–2.0","+","4.7–5.2","4.7–5.1","35–50","2.6–3.0","2.7–3.0","3.0–3.4","1.8–2.1","1.0–1.2","6.4–6.8","95–102","86–93","1–3","0.2–0.4"],
            "A.m. sahariensis": ["8.7–9.3","2.9–3.2","2.1–2.9","1.4–1.8","−","4.4–4.8","4.3–4.7","25–40","2.4–2.8","2.5–2.8","2.7–3.1","1.6–1.9","0.9–1.1","5.8–6.2","95–102","87–93","5–8","0.3–0.5"],
        }
        st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)

        section_header("📚 Références scientifiques")
        refs = [
            ("Ruttner F. (1988)", "Biogeography and Taxonomy of Honeybees. Springer, Berlin."),
            ("Cornuet JM & Fresnaye J. (1989)", "Etude biométrique de colonies d'abeilles d'Espagne et du Portugal. Apidologie 20(2):93–101."),
            ("Kandemir I. et al. (2011)", "Geometric morphometric analysis of honeybee wings. Apidologie 42:618–627."),
            ("Baylac M. et al. (2008)", "Geometric morphometrics in entomology: Basics and applications. Zookeys."),
            ("Chahbar N. et al. (2013)", "Population structure of North African honeybees. J. Apic. Res. 52(2):48–54."),
            ("Franck P. et al. (2000)", "Microsatellite analysis of sperm pooling in the honeybee. Heredity 85:81–87."),
        ]
        for author, ref in refs:
            st.markdown(f"▸ **{author}** — {ref}")

    with tab3:
        section_header("📊 Analyse comparative des mesures")
        df_m = st.session_state.data["morph_analyses"]

        if len(df_m) >= 2:
            fig_radar_comp = go.Figure()
            categories = ["L aile","Indice Ri","Glossa","Tomentum%","Ti-L","DI3"]
            ref_intermissa = [9.25, 2.4, 6.1, 37.5, 3.0, 1.7]
            ref_ligustica = [9.45, 2.8, 6.5, 52.5, 3.1, 1.8]
            ref_carnica = [9.45, 3.05, 6.6, 42.5, 3.2, 1.8]

            for _, row in df_m.iterrows():
                vals_raw = [row["L_aile_mm"], row["Ri"], row["Glossa_mm"], row["Tomentum_pct"], row["Ti_L_mm"], row["DI3_mm"]]
                maxv = [10.5, 4.0, 7.5, 70, 4.0, 2.5]
                vals_norm = [v/m*100 for v,m in zip(vals_raw, maxv)]
                fig_radar_comp.add_trace(go.Scatterpolar(
                    r=vals_norm+[vals_norm[0]], theta=categories+[categories[0]],
                    fill='toself', fillcolor=f'rgba(212,130,10,0.05)',
                    line=dict(width=1.5), name=f"{row['Ruche']} ({row['Taxon']})"
                ))

            fig_radar_comp.update_layout(
                polar=dict(
                    bgcolor='rgba(253,250,244,0.5)',
                    radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=8,color='#6B6040'),
                                    gridcolor='rgba(180,150,80,0.2)'),
                    angularaxis=dict(tickfont=dict(size=10,color='#4A3728'))
                ),
                showlegend=True, height=400,
                legend=dict(font=dict(size=10), bgcolor='rgba(255,255,255,0.8)'),
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=30,r=30,t=30,b=30)
            )
            st.plotly_chart(fig_radar_comp, use_container_width=True, config={"displayModeBar":False})

            section_header("📊 Distribution des mesures clés")
            fig_box = go.Figure()
            measures = {"L aile (mm)": "L_aile_mm", "Ri cubital": "Ri", "Glossa (mm)": "Glossa_mm"}
            colors_box = ["#D4820A","#F59E0B","#9B59B6"]
            for (label, col), color in zip(measures.items(), colors_box):
                fig_box.add_trace(go.Box(y=df_m[col], name=label,
                    marker_color=color, boxmean=True, line_width=1.5))
            fig_box.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                yaxis=dict(tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
                xaxis=dict(tickfont=dict(color='#4A3728')),
                margin=dict(l=10,r=10,t=10,b=10),
                legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Enregistrez au moins 2 analyses morphométriques pour voir les comparaisons.")

    with tab4:
        st.dataframe(st.session_state.data["morph_analyses"].sort_values("Date",ascending=False),
                     use_container_width=True, hide_index=True,
                     column_config={
                         "Confiance_pct": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
                     })

# ─────────────────────────────────────────────
# PAGE: CARACTÉRISATION (inchangée, adaptée à 'gelee_g')
# ─────────────────────────────────────────────
elif current_page == "caracterisation":
    st.markdown('<div class="page-title">📈 Caractérisation des Abeilles</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Profils de production · Langue & ailes · Résistance · Classification multiparamétrique</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Profils production", "👅 Caractères morpho.", "🛡️ Résistance & comportement", "🗺️ Carte de caractérisation"])

    with tab1:
        section_header("🎯 Classification par profil de production dominant")

        profils = df["Profil_prod"].value_counts().reset_index()
        profils.columns = ["Profil","Nombre"]

        c1, c2 = st.columns([1, 2])
        with c1:
            for _, row in profils.iterrows():
                icon = PROFIL_ICONS.get(row["Profil"], "🐝")
                color = PROFIL_COLORS.get(row["Profil"], "#D4820A")
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:16px 20px;border:1px solid rgba(180,150,80,0.2);
                            border-left:4px solid {color};margin-bottom:12px">
                    <div style="font-size:24px;margin-bottom:6px">{icon}</div>
                    <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#4A3728">{row['Nombre']}</div>
                    <div style="font-size:12px;font-weight:600;color:#6B6040;text-transform:uppercase;letter-spacing:0.06em">{row['Profil']}</div>
                </div>
                """, unsafe_allow_html=True)

        with c2:
            section_header("📊 Comparaison des profils")
            fig = go.Figure()
            metrics = {"Miel (kg)": "Miel_kg", "Pollen (kg×3)": "Pollen_kg", "Gelée R. (g/10)": "gelee_g"}
            for profil in df["Profil_prod"].unique():
                sub = df[df["Profil_prod"]==profil]
                fig.add_trace(go.Scatter(
                    x=list(metrics.keys()),
                    y=[sub["Miel_kg"].mean(), sub["Pollen_kg"].mean()*3, sub["gelee_g"].mean()/10],
                    name=f"{PROFIL_ICONS.get(profil,'')} {profil}",
                    mode='lines+markers', fill='toself',
                    line=dict(width=2), marker=dict(size=8)
                ))
            fig.update_layout(height=360, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                yaxis=dict(tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
                xaxis=dict(tickfont=dict(color='#4A3728',size=12)),
                legend=dict(font=dict(size=11), bgcolor='rgba(255,255,255,0.8)'),
                margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        section_header("🔬 Détail par ruche — Caractérisation complète")
        for _, r in df.iterrows():
            profil_color = PROFIL_COLORS.get(r["Profil_prod"], "#D4820A")
            profil_icon = PROFIL_ICONS.get(r["Profil_prod"], "🐝")
            with st.expander(f"{profil_icon} {r['Nom']} ({r['ID']}) — Profil : {r['Profil_prod']}"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f"""
                    <div style="background:#FDFAF4;border-radius:12px;padding:14px;border:1px solid rgba(180,150,80,0.2)">
                        <div style="font-size:11px;font-weight:600;color:#6B6040;text-transform:uppercase;margin-bottom:10px">🏭 Production</div>
                        <div style="margin-bottom:6px"><span style="color:#D4820A;font-weight:600">🍯 {r['Miel_kg']} kg</span> de miel</div>
                        <div style="margin-bottom:6px"><span style="color:#F59E0B;font-weight:600">🌼 {r['Pollen_kg']} kg</span> de pollen</div>
                        <div><span style="color:#9B59B6;font-weight:600">👑 {r['gelee_g']} g</span> de gelée royale</div>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"""
                    <div style="background:#FDFAF4;border-radius:12px;padding:14px;border:1px solid rgba(180,150,80,0.2)">
                        <div style="font-size:11px;font-weight:600;color:#6B6040;text-transform:uppercase;margin-bottom:10px">🔬 Morphologie</div>
                        <div style="margin-bottom:5px"><strong>Glossa :</strong> {r['Glossa_mm']} mm</div>
                        <div style="margin-bottom:5px"><strong>L. aile :</strong> {r['L_aile_mm']} mm</div>
                        <div style="margin-bottom:5px"><strong>Ri cubital :</strong> {r['Ri']}</div>
                        <div><strong>Tomentum :</strong> {r['Tomentum_pct']}%</div>
                    </div>""", unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"""
                    <div style="background:#FDFAF4;border-radius:12px;padding:14px;border:1px solid rgba(180,150,80,0.2)">
                        <div style="font-size:11px;font-weight:600;color:#6B6040;text-transform:uppercase;margin-bottom:10px">🧬 Génétique</div>
                        <div style="margin-bottom:5px"><strong>Race :</strong> {r['Race']}</div>
                        <div style="margin-bottom:5px"><strong>VSH :</strong> {r['VSH_pct']}%</div>
                        <div style="margin-bottom:5px"><strong>Douceur :</strong> {r['Douceur']}%</div>
                        <div><strong>Éco. hiv. :</strong> {r['Economie_hiv']}%</div>
                    </div>""", unsafe_allow_html=True)
                st.plotly_chart(production_radar(r), use_container_width=True, config={"displayModeBar":False})

    with tab2:
        section_header("👅 Caractères morphologiques — Langue & Ailes")

        st.markdown(alert("🔬", """<strong>Importance de la longueur de la glossa (langue)</strong> : La longueur de la langue est le principal caractère 
            discriminant entre les races méditerranéennes. <em>A.m. ligustica</em> (6.3–6.7mm) et <em>A.m. carnica</em> (6.4–6.8mm) ont des langues 
            plus longues qu'<em>A.m. intermissa</em> (5.9–6.3mm) et <em>A.m. sahariensis</em> (5.8–6.2mm). 
            La longueur de la langue est corrélée à l'accessibilité aux nectars de fleurs à corolles profondes.""", "alert-info"), unsafe_allow_html=True)

        c_g, c_a = st.columns(2)

        with c_g:
            section_header("👅 Distribution de la longueur de la glossa")
            fig_g = go.Figure()
            for race in df["Race"].unique():
                sub = df[df["Race"]==race]
                color = {"A. m. intermissa":"#D4820A","A. m. sahariensis":"#9B59B6",
                         "A. m. ligustica":"#3b82f6","A. m. carnica":"#22c55e","Hybride":"#6b7280"}.get(race,"#6b7280")
                fig_g.add_trace(go.Box(y=sub["Glossa_mm"], name=race[:15], marker_color=color,
                    boxmean=True, jitter=0.3, pointpos=-1.8,
                    marker=dict(size=6, opacity=0.6)))

            ref_ranges = {
                "intermissa": (5.9, 6.3, "#D4820A"),
                "ligustica": (6.3, 6.7, "#3b82f6"),
                "carnica": (6.4, 6.8, "#22c55e"),
                "sahariensis": (5.8, 6.2, "#9B59B6"),
            }
            for name, (lo, hi, col) in ref_ranges.items():
                fig_g.add_hrect(y0=lo, y1=hi, fillcolor=col, opacity=0.04, line_width=0)

            fig_g.update_layout(height=360, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                yaxis=dict(title="Glossa (mm)", tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
                xaxis=dict(tickfont=dict(color='#4A3728', size=10)),
                margin=dict(l=10,r=10,t=20,b=10),
                legend=dict(font=dict(size=9), bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar":False})

        with c_a:
            section_header("✈️ Longueur aile antérieure & Indice cubital")
            fig_wing = go.Figure()
            for race in df["Race"].unique():
                sub = df[df["Race"]==race]
                color = {"A. m. intermissa":"#D4820A","A. m. sahariensis":"#9B59B6",
                         "A. m. ligustica":"#3b82f6","A. m. carnica":"#22c55e","Hybride":"#6b7280"}.get(race,"#6b7280")
                fig_wing.add_trace(go.Scatter(
                    x=sub["L_aile_mm"], y=sub["Ri"], mode='markers+text',
                    text=sub["ID"], textposition='top center', textfont=dict(size=9,color='#4A3728'),
                    marker=dict(size=12, color=color, opacity=0.8, line=dict(color='white',width=1.5)),
                    name=race[:15]
                ))

            fig_wing.add_vrect(x0=8.9, x1=9.6, fillcolor="#D4820A", opacity=0.04, line_width=0, annotation_text="intermissa L", annotation_position="top left")
            fig_wing.update_layout(height=360, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                xaxis=dict(title="L aile ant. (mm)", tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
                yaxis=dict(title="Indice cubital Ri", tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
                legend=dict(font=dict(size=9), bgcolor='rgba(255,255,255,0.8)'),
                margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(fig_wing, use_container_width=True, config={"displayModeBar":False})

        section_header("📊 Tomentum (bande dorée abdominale) — Caractère discriminant")
        st.markdown("""<div style="font-size:13px;color:#6B6040;line-height:1.7;margin-bottom:16px">
        Le tomentum (bande de poils clairs sur le 4ème tergite abdominal) est un indicateur de pigmentation. 
        Un tomentum large (>45%) est typique des races italiennes et carnioliennes. Les races nord-africaines 
        (<em>intermissa</em>, <em>sahariensis</em>) ont un tomentum plus étroit (25–45%).
        </div>""", unsafe_allow_html=True)
        fig_tom = go.Figure()
        df_sorted = df.sort_values("Tomentum_pct")
        colors_tom = ["#D4820A" if "intermissa" in r else "#9B59B6" if "sahariensis" in r else
                      "#3b82f6" if "ligustica" in r else "#22c55e" if "carnica" in r else "#6b7280"
                      for r in df_sorted["Race"]]
        fig_tom.add_trace(go.Bar(x=df_sorted["Nom"], y=df_sorted["Tomentum_pct"],
            marker_color=colors_tom, text=[f"{v}%" for v in df_sorted["Tomentum_pct"]],
            textposition='outside', textfont=dict(size=11,color='#4A3728')))
        fig_tom.add_hline(y=45, line_dash="dash", line_color="#3b82f6", annotation_text="Seuil ligustica/carnica (45%)")
        fig_tom.add_hline(y=30, line_dash="dash", line_color="#D4820A", annotation_text="Seuil min. intermissa (30%)")
        fig_tom.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
            yaxis=dict(title="Tomentum (%)", range=[0,75], tickfont=dict(color='#6B6040')),
            xaxis=dict(tickfont=dict(color='#4A3728')),
            margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig_tom, use_container_width=True, config={"displayModeBar":False})

    with tab3:
        section_header("🛡️ Résistance au Varroa (VSH) & Comportement")

        st.markdown(alert("🛡️", """<strong>VSH (Varroa Sensitive Hygiene)</strong> : Comportement héréditaire par lequel les abeilles détectent et 
            éliminent les varroas reproductrices dans les cellules fermées. Un score VSH ≥70% indique une bonne résistance naturelle. 
            Sélectionner pour ce caractère réduit significativement la dépendance aux traitements chimiques.""", "alert-info"), unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            section_header("📊 Score VSH par ruche")
            df_vsh = df.sort_values("VSH_pct")
            colors_vsh = ["#ef4444" if v < 60 else "#f59e0b" if v < 70 else "#22c55e" for v in df_vsh["VSH_pct"]]
            fig_vsh = go.Figure(go.Bar(
                x=df_vsh["VSH_pct"], y=df_vsh["Nom"], orientation='h',
                marker_color=colors_vsh,
                text=[f"{v}%" for v in df_vsh["VSH_pct"]], textposition='inside',
                textfont=dict(color='white',size=11)
            ))
            fig_vsh.add_vline(x=70, line_dash="dash", line_color="#6b7280", annotation_text="Seuil cible (70%)")
            fig_vsh.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                xaxis=dict(range=[0,105], title="VSH (%)", tickfont=dict(color='#6B6040')),
                yaxis=dict(tickfont=dict(color='#4A3728',size=12)),
                margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(fig_vsh, use_container_width=True, config={"displayModeBar":False})

        with c2:
            section_header("📊 Matrice des critères de sélection")
            criteria = ["VSH%","Douceur","Éco.hiv.","Anti-essaimage\n(100−%)"]
            fig_crit = go.Figure()
            for _, r in df.iterrows():
                vals = [r["VSH_pct"], r["Douceur"], r["Economie_hiv"], 100-r["Essaimage_pct"]]
                fig_crit.add_trace(go.Scatter(
                    x=criteria+[criteria[0]], y=vals+[vals[0]],
                    mode='lines', name=r["Nom"],
                    line=dict(width=1.5), fill='toself', fillcolor=f'rgba(212,130,10,0.04)'
                ))
            fig_crit.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                yaxis=dict(range=[0,110],title="Score (%)",tickfont=dict(color='#6B6040'),gridcolor='rgba(180,150,80,0.1)'),
                xaxis=dict(tickfont=dict(color='#4A3728')),
                legend=dict(font=dict(size=9),bgcolor='rgba(255,255,255,0.8)'),
                margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(fig_crit, use_container_width=True, config={"displayModeBar":False})

        section_header("🏆 Classement général des ruches")
        df["Score_VSH"] = df["VSH_pct"]
        df["Score_prod"] = (df["Miel_kg"]/20*40 + df["Pollen_kg"]/5*20 + df["gelee_g"]/200*20 +
                            df["VSH_pct"]/100*10 + df["Douceur"]/100*10).clip(0,100).round(1)
        df_rank = df[["Nom","Race","Profil_prod","Score_prod","VSH_pct","Douceur","Varroa_pct"]].sort_values("Score_prod",ascending=False)
        df_rank.columns = ["Ruche","Race","Profil","Score global","VSH%","Douceur%","Varroa%"]
        st.dataframe(df_rank, use_container_width=True, hide_index=True,
            column_config={
                "Score global": st.column_config.ProgressColumn(format="%.1f/100", min_value=0, max_value=100),
                "VSH%": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
                "Varroa%": st.column_config.NumberColumn(format="%.1f%%"),
            })

    with tab4:
        section_header("🗺️ Carte de caractérisation multiparamétrique")
        st.markdown("""<div style="font-size:13px;color:#6B6040;line-height:1.7;margin-bottom:16px">
        Visualisation en espace ACP (Analyse en Composantes Principales) des ruches selon leurs caractères morphométriques et de production.
        Les clusters représentent les groupes raciaux naturels.</div>""", unsafe_allow_html=True)

        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler

            features = ["L_aile_mm","Ri","Glossa_mm","Tomentum_pct","Pollen_kg","Miel_kg","gelee_g","VSH_pct"]
            X = df[features].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            pca = PCA(n_components=2, random_state=42)
            X_pca = pca.fit_transform(X_scaled)

            color_map = {"A. m. intermissa":"#D4820A","A. m. sahariensis":"#9B59B6",
                         "A. m. ligustica":"#3b82f6","A. m. carnica":"#22c55e","Hybride":"#6b7280"}

            fig_pca = go.Figure()
            for race in df["Race"].unique():
                mask = df["Race"]==race
                fig_pca.add_trace(go.Scatter(
                    x=X_pca[mask,0], y=X_pca[mask,1],
                    mode='markers+text',
                    text=df.loc[mask,"ID"].values,
                    textposition='top center', textfont=dict(size=10,color='#4A3728'),
                    marker=dict(size=18, color=color_map.get(race,"#6b7280"), opacity=0.8,
                                symbol="hexagon", line=dict(color='white',width=2)),
                    name=race
                ))
            fig_pca.update_layout(
                height=440, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
                xaxis=dict(title=f"CP1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)",
                           tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
                yaxis=dict(title=f"CP2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)",
                           tickfont=dict(color='#6B6040'), gridcolor='rgba(180,150,80,0.1)'),
                legend=dict(font=dict(size=11), bgcolor='rgba(255,255,255,0.85)',
                            bordercolor='rgba(180,150,80,0.3)', borderwidth=1),
                margin=dict(l=10,r=10,t=30,b=10)
            )
            st.plotly_chart(fig_pca, use_container_width=True, config={"displayModeBar":False})

            var_explained = pd.DataFrame({
                "Composante": [f"CP{i+1}" for i in range(2)],
                "Variance expliquée (%)": [f"{v*100:.1f}%" for v in pca.explained_variance_ratio_],
                "Variance cumulée (%)": [f"{pca.explained_variance_ratio_[:i+1].sum()*100:.1f}%" for i in range(2)],
            })
            st.dataframe(var_explained, use_container_width=True, hide_index=True)

        except ImportError:
            st.info("scikit-learn requis pour l'analyse ACP. Installez-le avec : pip install scikit-learn")

# ─────────────────────────────────────────────
# PAGE: GÉNÉTIQUE (inchangée)
# ─────────────────────────────────────────────
elif current_page == "genetique":
    st.markdown('<div class="page-title">🧬 Génétique & Sélection</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Lignées reines · Élevage · VSH · Marqueurs génétiques · Programme de sélection</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    tab1, tab2 = st.tabs(["👑 Registre des reines", "🧬 Programme de sélection"])

    with tab1:
        st.dataframe(df[["Reine_id","ID","Race","VSH_pct","Douceur","Economie_hiv","Essaimage_pct","Profil_prod"]].rename(
            columns={"Reine_id":"ID Reine","ID":"Ruche","VSH_pct":"VSH%","Douceur":"Douceur%",
                     "Economie_hiv":"Éco. hiv.%","Essaimage_pct":"Essaimage%","Profil_prod":"Profil"}),
            use_container_width=True, hide_index=True,
            column_config={
                "VSH%": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
                "Douceur%": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
            })

        section_header("📊 Critères de sélection — Vue d'ensemble")
        criteria = ["VSH (Résistance Varroa)","Douceur","Productivité miel","Économie hivernale","Anti-essaimage"]
        values = [df["VSH_pct"].mean(), df["Douceur"].mean(), df["Miel_kg"].mean()/20*100,
                  df["Economie_hiv"].mean(), 100-df["Essaimage_pct"].mean()]
        colors_c = ["#22c55e","#3b82f6","#D4820A","#9B59B6","#f59e0b"]

        for c, v, col in zip(criteria, values, colors_c):
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px">
                    <span style="color:#4A3728;font-weight:500">{c}</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-weight:600;color:#4A3728">{v:.0f}%</span>
                </div>
                <div style="height:10px;background:#F5EDD8;border-radius:5px;overflow:hidden">
                    <div style="height:100%;width:{v}%;background:{col};border-radius:5px;transition:width 0.5s"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        section_header("🧬 Programme de sélection massale")
        st.markdown(alert("🧬", """Le programme de sélection massale combine l'évaluation des colonies sur plusieurs générations 
            avec des mesures morphométriques et des tests de comportement. L'objectif principal est l'amélioration de la 
            résistance naturelle au Varroa (VSH) tout en maintenant la productivité et la douceur.""", "alert-info"), unsafe_allow_html=True)

        st.markdown("**🏆 Ruches candidates à l'élevage de reines (Top 3)**")
        top3 = df.nlargest(3, "VSH_pct")
        for i, (_, r) in enumerate(top3.iterrows()):
            medal = ["🥇","🥈","🥉"][i]
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:16px;border:1px solid rgba(180,150,80,0.2);
                        margin-bottom:10px;display:flex;align-items:center;gap:16px">
                <div style="font-size:28px">{medal}</div>
                <div style="flex:1">
                    <div style="font-family:'Playfair Display',serif;font-size:16px;font-weight:700">{r['Nom']} ({r['ID']})</div>
                    <div style="font-size:12px;color:#6B6040">{r['Race']} · VSH: {r['VSH_pct']}% · Douceur: {r['Douceur']}%</div>
                </div>
                <div style="text-align:center">
                    <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:#22c55e">{r['VSH_pct']}%</div>
                    <div style="font-size:10px;color:#6B6040;text-transform:uppercase;letter-spacing:0.07em">VSH</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: FLORE (inchangée)
# ─────────────────────────────────────────────
elif current_page == "flore":
    st.markdown('<div class="page-title">🌸 Flore Mellifère</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Calendrier de floraison · Valeur apicole · Région de l\'Oranie — Algérie</div>', unsafe_allow_html=True)

    flore_data = {
        "Espèce": ["🌳 Jujubier (Ziziphus lotus)","🌿 Romarin (Rosmarinus off.)","🍊 Oranger (Citrus sinensis)",
                   "🌼 Lavande (Lavandula sp.)","🌱 Thym (Thymus vulgaris)","🌳 Eucalyptus (E. globulus)",
                   "🌻 Tournesol (H. annuus)","🌺 Chardon (Cynara sp.)","🌱 Alfa (Stipa tenacissima)",
                   "🌼 Phacélie","🫒 Olivier (Olea europaea)","🌿 Sainfoin (Onobrychis sp.)"],
        "Floraison": ["Mai–Juin","Fév–Avr","Avr–Mai","Juin–Jul","Avr–Juin","Nov–Jan","Juil–Août","Mai–Jul","Mar–Avr","Avr–Jun","Avr–Mai","Mai–Jun"],
        "Nectarifère": ["★★★★★","★★★★","★★★★★","★★★★","★★★★","★★★★","★★★","★★★","★★","★★★★★","★★★","★★★★"],
        "Pollinifère": ["★★★★","★★★","★★★★","★★★★","★★★","★★★★","★★★★★","★★★","★★★★","★★★★","★★★","★★★"],
        "Valeur mellifère": ["Excellente","Très bonne","Excellente","Très bonne","Très bonne","Bonne","Bonne","Moyenne","Pollinifère","Excellente","Bonne","Bonne"],
        "Habitat": ["Steppes, maquis","Garrigues","Vergers","Garrigues","Zones sèches","Forêts plantées","Cultures","Steppes","Steppes arides","Cultures","Vergers","Cultures"],
        "Miellée principale": ["Oui","Non","Oui","Non","Non","Partielle","Non","Non","Non","Oui","Non","Non"],
    }
    df_flore = pd.DataFrame(flore_data)
    st.dataframe(df_flore, use_container_width=True, hide_index=True)

    section_header("📅 Calendrier de disponibilité mellifère")
    mois = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
    disponibilite = [15,35,50,80,95,90,65,40,25,15,20,18]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mois, y=disponibilite, fill='tozeroy', name="Disponibilité nectar",
        fillcolor='rgba(212,130,10,0.15)', line=dict(color='#D4820A',width=2.5),
        mode='lines+markers', marker=dict(size=7,color='#D4820A')))
    fig.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
        yaxis=dict(title="Indice de disponibilité",tickfont=dict(color='#6B6040'),gridcolor='rgba(180,150,80,0.1)'),
        xaxis=dict(tickfont=dict(color='#4A3728')),
        margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ─────────────────────────────────────────────
# PAGE: MÉTÉO (inchangée)
# ─────────────────────────────────────────────
elif current_page == "meteo":
    st.markdown('<div class="page-title">🌤️ Météo & Miellée</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Conditions de butinage · Prévisions · Indice de miellée · Tlemcen — Algérie</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    meteos = [
        ("Aujourd'hui","22°C","☀️ Ensoleillé","65%","12 km/h","8/10","linear-gradient(135deg,#2D4A1E,#3D6B2C)"),
        ("Demain","19°C","⛅ Nuageux","72%","20 km/h","5/10","linear-gradient(135deg,#2D5A3D,#3D6B2C)"),
        ("Après-demain","16°C","🌧️ Pluie","88%","35 km/h","1/10","linear-gradient(135deg,#3A2F1E,#5A4030)"),
    ]
    for col, (jour, temp, cond, hum, vent, miel, grad) in zip([c1,c2,c3], meteos):
        with col:
            st.markdown(f"""
            <div style="background:{grad};border-radius:18px;padding:22px;color:white;margin-bottom:16px">
                <div style="font-size:10px;opacity:0.6;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px">{jour}</div>
                <div style="font-family:'Playfair Display',serif;font-size:44px;font-weight:700;line-height:1">{temp}</div>
                <div style="font-size:14px;opacity:0.85;margin-top:4px">{cond}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:16px;
                            padding-top:14px;border-top:1px solid rgba(255,255,255,0.15)">
                    <div style="text-align:center"><div style="font-size:16px;font-weight:600">{hum}</div>
                        <div style="font-size:9px;opacity:0.55;text-transform:uppercase">Humidité</div></div>
                    <div style="text-align:center"><div style="font-size:16px;font-weight:600">{vent}</div>
                        <div style="font-size:9px;opacity:0.55;text-transform:uppercase">Vent</div></div>
                    <div style="text-align:center"><div style="font-size:16px;font-weight:600">{miel}</div>
                        <div style="font-size:9px;opacity:0.55;text-transform:uppercase">Miellée</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

    section_header("📊 Indice de butinage — 7 derniers jours")
    jours = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
    indice = [4,8,9,8,6,5,4]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=jours, y=indice, fill='tozeroy',
        fillcolor='rgba(212,130,10,0.15)', line=dict(color='#D4820A',width=2.5),
        mode='lines+markers', marker=dict(size=10,color='#D4820A',line=dict(color='white',width=2)),
        text=[f"{v}/10" for v in indice], textposition='top center', textfont=dict(size=11,color='#4A3728')))
    fig.update_layout(height=240, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(253,250,244,0.5)',
        yaxis=dict(range=[0,11],title="Indice (0–10)",tickfont=dict(color='#6B6040'),gridcolor='rgba(180,150,80,0.1)'),
        xaxis=dict(tickfont=dict(color='#4A3728')),
        margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ─────────────────────────────────────────────
# PAGE: RAPPORTS (inchangée)
# ─────────────────────────────────────────────
elif current_page == "rapports":
    st.markdown('<div class="page-title">📋 Rapports & Exports</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Rapports réglementaires · Analyses statistiques · Export données</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]
    rec = st.session_state.data["recoltes"]

    section_header("📊 Résumé de la saison 2024")
    c1, c2, c3 = st.columns(3)
    with c1:
        miel_total = df["Miel_kg"].sum()
        pol_total = df["Pollen_kg"].sum()
        gr_total = df["gelee_g"].sum()
        ca_total = rec.apply(lambda r: r["Quantite_kg"]*r["Prix_kg"], axis=1).sum()
        st.markdown(f"""
        <div class="morph-card">
            <div style="font-weight:700;color:#D4820A;margin-bottom:12px">🍯 Production</div>
            <div class="measure-row"><span>Miel total</span><span class="measure-val-ok">{miel_total:.0f} kg</span></div>
            <div class="measure-row"><span>Pollen total</span><span class="measure-val-ok">{pol_total:.1f} kg</span></div>
            <div class="measure-row"><span>Gelée royale</span><span class="measure-val-ok">{gr_total} g</span></div>
            <div class="measure-row"><span>CA estimé</span><span class="measure-val-ok">{ca_total:,.0f} DA</span></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        varroa_moy = df["Varroa_pct"].mean()
        vsh_moy = df["VSH_pct"].mean()
        nb_insp = len(st.session_state.data["inspections"])
        st.markdown(f"""
        <div class="morph-card">
            <div style="font-weight:700;color:#22c55e;margin-bottom:12px">🩺 Santé</div>
            <div class="measure-row"><span>Varroa moyen</span><span class="{'measure-val-ok' if varroa_moy<2 else 'measure-val-warn'}">{varroa_moy:.1f}%</span></div>
            <div class="measure-row"><span>VSH moyen</span><span class="{'measure-val-ok' if vsh_moy>70 else 'measure-val-warn'}">{vsh_moy:.0f}%</span></div>
            <div class="measure-row"><span>Traitements</span><span class="measure-val-ok">{len(st.session_state.data['traitements'])}</span></div>
            <div class="measure-row"><span>Inspections</span><span class="measure-val-ok">{nb_insp}</span></div>
        </div>""", unsafe_allow_html=True)
    with c3:
        nb_morph = len(st.session_state.data["morph_analyses"])
        race_dom = df["Race"].value_counts().idxmax() if len(df)>0 else "—"
        conf_moy = st.session_state.data["morph_analyses"]["Confiance_pct"].mean() if len(st.session_state.data["morph_analyses"])>0 else 0
        st.markdown(f"""
        <div class="morph-card">
            <div style="font-weight:700;color:#9B59B6;margin-bottom:12px">🔬 Science</div>
            <div class="measure-row"><span>Analyses morpho.</span><span class="measure-val-ok">{nb_morph}</span></div>
            <div class="measure-row"><span>Race dominante</span><span class="measure-val-ok" style="font-size:11px">{race_dom[:15]}</span></div>
            <div class="measure-row"><span>Confiance moy.</span><span class="measure-val-ok">{conf_moy:.0f}%</span></div>
            <div class="measure-row"><span>Profils actifs</span><span class="measure-val-ok">{df['Profil_prod'].nunique()}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("⬇️ Exports disponibles")
    c_ex1, c_ex2, c_ex3, c_ex4 = st.columns(4)

    export_items = [
        ("📊", "Données ruches", "CSV complet", st.session_state.data["ruches"]),
        ("🔬", "Morphométrie", "CSV analyses", st.session_state.data["morph_analyses"]),
        ("🍯", "Récoltes", "CSV production", st.session_state.data["recoltes"]),
        ("💊", "Traitements", "CSV vétérinaire", st.session_state.data["traitements"]),
    ]
    for col, (icon, title, subtitle, data) in zip([c_ex1,c_ex2,c_ex3,c_ex4], export_items):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:14px;padding:20px;text-align:center;
                        border:1px solid rgba(180,150,80,0.2);margin-bottom:12px">
                <div style="font-size:32px;margin-bottom:10px">{icon}</div>
                <div style="font-weight:600;font-size:14px;margin-bottom:4px">{title}</div>
                <div style="font-size:11px;color:#6B6040">{subtitle}</div>
            </div>""", unsafe_allow_html=True)
            csv = data.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"⬇ Télécharger",
                data=csv,
                file_name=f"apitrack_{title.lower().replace(' ','_')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ─────────────────────────────────────────────
# PAGE: ALERTES (inchangée)
# ─────────────────────────────────────────────
elif current_page == "alertes":
    st.markdown('<div class="page-title">🚨 Alertes & Notifications</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Surveillance en temps réel · Priorisation intelligente · Actions correctives</div>', unsafe_allow_html=True)

    df = st.session_state.data["ruches"]

    alertes_auto = []
    for _, r in df.iterrows():
        if r["Varroa_pct"] > 3:
            alertes_auto.append(("🔴","danger",f"CRITIQUE — {r['Nom']} ({r['ID']}) : Varroa {r['Varroa_pct']}% — Traitement urgent requis."))
        elif r["Varroa_pct"] > 2:
            alertes_auto.append(("🟠","warning",f"ATTENTION — {r['Nom']} ({r['ID']}) : Varroa {r['Varroa_pct']}% — Surveiller."))
        if r["Statut"] == "Critique":
            alertes_auto.append(("🔴","danger",f"CRITIQUE — {r['Nom']} ({r['ID']}) : Statut général critique. Inspection urgente."))
        if r["VSH_pct"] < 60:
            alertes_auto.append(("🟡","warning",f"SÉLECTION — {r['Nom']} ({r['ID']}) : VSH {r['VSH_pct']}% — Sous le seuil de 60%. Renouveler la reine."))
        if r["gelee_g"] > 150 and r["Profil_prod"] == "Gelée Royale":
            alertes_auto.append(("👑","royal",f"RÉCOLTE — {r['Nom']} ({r['ID']}) : Excellente productrice de gelée royale ({r['gelee_g']}g). Planifier la prochaine récolte."))

    alertes_auto.append(("📦","info","STOCK — Cire gaufrée : Niveau critique (1.2 kg restant, seuil : 5 kg). Commander rapidement."))
    alertes_auto.append(("📅","info","RAPPEL : Traitement anti-varroa hivernal recommandé. Prévoir entre novembre et décembre."))
    alertes_auto.append(("✅","success","Bonne nouvelle : 6 colonies montrent un VSH > 70%. Programme de sélection en bonne voie !"))

    cls_map = {"danger":"alert-danger","warning":"alert-warning","success":"alert-success","info":"alert-info","royal":"alert-royal"}

    for icon, level, txt in alertes_auto:
        st.markdown(alert(icon, txt, cls_map.get(level,"alert-info")), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:32px 0 16px;font-size:12px;color:#9B8860;border-top:1px solid rgba(180,150,80,0.15);margin-top:40px">
    <strong style="font-family:'Playfair Display',serif;font-size:14px;color:#4A3728">ApiTrack Pro</strong> · 
    Plateforme Apicole Professionnelle · Version 2.0<br>
    Morphométrie selon <em>Ruttner (1988)</em> · Données de référence <em>Chahbar et al. (2013)</em> · 
    Région de l'Oranie, Algérie<br><br>
    🐝 Développé pour l'apiculture scientifique et professionnelle
</div>
""", unsafe_allow_html=True)
