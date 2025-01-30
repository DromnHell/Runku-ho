STANDARD_IGNORED_CLASSES = [
    # Navigation and structure
    "mw-navigation",  # MediaWiki navigation elements
    "mw-footer",  # Footer of the page
    "mw-sidebar",  # Sidebar navigation
    "mw-header",  # Page header
    "navbox",  # Navigational boxes
    "toc",  # Table of contents
    "sidebar",  # General sidebar
    "breadcrumb",  # Breadcrumb navigation
    "pagination",  # Pagination controls
    "footer",  # Generic footer
    "header",  # Generic header

    # Annotations and metadata
    "mw-references-wrap",  # Wrapper for references
    "reference",  # Individual references
    "citation",  # Citation blocks
    "metadata",  # Metadata information
    "footnote",  # Footnotes
    "annotation",  # Annotations
    "ws-noexport",  # Content not meant for export

    # Ads and external content
    "ad-container",  # Container for ads
    "ad-banner",  # Banner ads
    "sponsored",  # Sponsored content
    "affiliate",  # Affiliate links

    # Images and galleries
    "thumb",  # Thumbnails
    "gallery",  # Galleries
    "gallerytext",  # Text under galleries
    "image-container",  # Containers for images

    # Interactive or dynamic content
    "tooltip",  # Tooltip elements
    "dropdown",  # Dropdown menus
    "popup",  # Popup elements
    "hover",  # Hover effects

    # Content for printing or exporting
    "no-print",  # Hidden in print views
    "print-only",  # Visible only in print views
    "export-ignore",  # Ignored during export
    "ws-noexport",  # WikiSource-specific no-export class

    # Decorative or unnecessary content
    "spacer",  # Spacers
    "clearfix",  # Clearfix utility class
    "empty",  # Empty containers
    "divider",  # Decorative dividers

    # Languages and translations
    "interwiki",  # Interlanguage links
    "language-selector",  # Dropdown for language selection
    "lang-switcher",  # Language switcher
    "translation-header",  # Header for translation content

    # CMS or editing-related elements
    "editsection",  # Edit section links
    "page-tools",  # Tools for editing or page management
    "action-buttons",  # Buttons for page actions
    "mw-editsection",  # MediaWiki edit section links
    "mw-history",  # Page history controls

    # MediaWiki-specific elements (as seen on Ryzom Wiki)
    "mw-allpages-nav",  # Navigation for all pages
    "mw-category-generated",  # Auto-generated category lists
    "mw-parser-output",  # General parser output
    "category"  # Categories
]

CONTENT_PORTAL_BOX_KEYS_STYLE = ['padding:0em',
                                'border:thin inset #0ff',
                                'color:#000']

BANNER_PORTAL_BOX_KEYS_STYLE = ['font-weight:bold',
                             'text-shadow: #333 .1em .1em .1em, #fff -.1em -.1em .1em',
                             'text-align: center',
                             'color: #000',
                             'margin: 0em',
                             'border-width: medium',
                             'padding:0.1em',
                             'font-size: 1em']

OTHER_KEYS_STYLE = ['border-radius: 1em',
                                'color: #000',
                                'padding: 0em 1em',
                                'border: none',
                                'text-align: right',
                                'margin: 0em']

IGNORED_DIV_RULES = {
    "classes": ["subpagelist"] + STANDARD_IGNORED_CLASSES,
    "ids": ["tradbox","toc"],
    "summaries": [],
    "styles": [CONTENT_PORTAL_BOX_KEYS_STYLE,
               BANNER_PORTAL_BOX_KEYS_STYLE,
               OTHER_KEYS_STYLE,
               "margin:1em 0em 2em 0em; padding:0.1em; border: none groove #fa5; border-radius:1em; background: #fda; background-image: linear-gradient(to top, #500 0%, #a50 10%, #fda 20% 80%, #fb7 90%, #fa5 100%); color: #fa5; text-align: center;",
               "text-align:right;font-weight: normal; font-size:xx-small;font-variant:none;font-style:italic;text-shadow:none",
               "padding-top:.5em;text-align:center;font-weight: bold; font-size: 150%;font-variant: small-caps;",
               "position:absolute; left:40px; top:2px; right:0px",
               "text-align: right; font-size: smaller;",
               "text-align:center;",
               "text-align:center"]
}

AMBRE_TABLE_KEYS_STYLE = [
    "float: right",
    "width:25%",
    "max-width:30%",
    "margin: 0.1em",
    "overflow: auto",
    "border: thick outset #C90",
    "border-radius:1em",
    "padding: 0.1em"
]

GENEALOGY_SUMMARIES = [
    "Genealogy of the Matis Royal Family",
    "Imperial genealogy",
    "Genealogy of Dexton",
    "Généalogie Cerakos II",
    "Genealogy of Abylus"
]

IGNORED_TABLE_RULES = {
    "classes": ["mw-gallery-packed", "mw-collapsible", "mw-babel-wrapper"] + STANDARD_IGNORED_CLASSES,
    "ids": [],
    "summaries": GENEALOGY_SUMMARIES,
    "styles": [AMBRE_TABLE_KEYS_STYLE,
               "float: right; width:25%; max-width:30%; margin: 0.1em; overflow: auto; border: thick outset #C90; border-radius:1em; padding: 0.1em;background-color: #C90; background-color: rgba(255, 165, 0, 0.5); background-image: radial-gradient(rgba(255, 255, 255, 0.2),rgba(255, 165, 0, 0.5)); cellspacing: 0.01em; cellpadding:0.01em; vertical-align:center;",
               "border-style:solid;border-width:1px;border-color:#111111;background-color:#FFEFD4; margin:1em; padding:0 .5em; border: #099 medium outset;border-radius:.5em;background: linear-gradient(to right, #fee , #efe, #eef);",
               "margin: 0 0 1em 1em; border: 1px solid #999; border-right-width: 2px; border-bottom-width: 2px; background-color: #F2D19C; maxwidth=33%",
               "border:1px solid #336600; font-size:90%; width:100%; text-align:center; clear:both;",
               "background-color: transparent;",
               "background-color: transparent",
               "margin:auto;",
               "margin:auto"]
}

IGNORED_LIST_RULES = {
    "classes": [] + STANDARD_IGNORED_CLASSES,
    "ids": [],
    "summaries": [],
    "styles": []
}

URL_TO_NOT_SCRAP = [
    "https://fr.wiki.ryzom.com/wiki/ARK",
    "https://fr.wiki.ryzom.com/wiki/A_propos_de_la_connexion,_des_identifiants",
    "https://fr.wiki.ryzom.com/wiki/Team_Administration_List",
    "https://fr.wiki.ryzom.com/wiki/Actualit%C3%A9s",
    "https://fr.wiki.ryzom.com/wiki/Guide_de_r%C3%A9daction/Aide_officielle_Wiki",
    "https://fr.wiki.ryzom.com/wiki/Ambres_d%27Animations",
    "https://fr.wiki.ryzom.com/wiki/Anlor_Winn",
    "https://fr.wiki.ryzom.com/wiki/Anniversaire_15_ans",
    "https://fr.wiki.ryzom.com/wiki/Anniversaire_de_Ryzom",
    "https://fr.wiki.ryzom.com/wiki/Anniversaires",
    "https://fr.wiki.ryzom.com/wiki/Annonces-2014-2015",
    "https://fr.wiki.ryzom.com/wiki/Apps",
    "https://fr.wiki.ryzom.com/wiki/Appartement",
    "https://fr.wiki.ryzom.com/wiki/Artisanat",
    "https://fr.wiki.ryzom.com/wiki/Atys_Mag",
    "https://fr.wiki.ryzom.com/wiki/Atyso%C3%ABl",
    "https://fr.wiki.ryzom.com/wiki/BM",
    "https://fr.wiki.ryzom.com/wiki/Backstage",
    "https://fr.wiki.ryzom.com/wiki/Brouillon_language",
    "https://fr.wiki.ryzom.com/wiki/Utilisatrice:Craftjenn/Bug_mission",
    "https://fr.wiki.ryzom.com/wiki/Bugs",
    "https://fr.wiki.ryzom.com/wiki/Building_Ryzom_Client_On_Debian_(Stripped_Version)",
    "https://fr.wiki.ryzom.com/wiki/Bunny_Tools",
    "https://fr.wiki.ryzom.com/wiki/Bureau_AFC",
    "https://fr.wiki.ryzom.com/wiki/CA_Invasion_%C3%A0_Fairhaven",
    "https://fr.wiki.ryzom.com/wiki/CA_Invasion_%C3%A0_Pyr",
    "https://fr.wiki.ryzom.com/wiki/CA_Menaces_Violettes",
    "https://fr.wiki.ryzom.com/wiki/Utilisatrice:Craftjenn/",
    "https://fr.wiki.ryzom.com/wiki/Customer_Support_Representative",
    "https://fr.wiki.ryzom.com/wiki/Camps_d%27observation_de_la_menace_Kitine/HRP",
    "https://fr.wiki.ryzom.com/wiki/Carte_d%27Atys",
    "https://fr.wiki.ryzom.com/wiki/Cat%C3%A9gorisation",
    "https://fr.wiki.ryzom.com/wiki/SOS/Cat%C3%A9goriser_une_image",
    "https://fr.wiki.ryzom.com/wiki/CeB",
    "https://fr.wiki.ryzom.com/wiki/Cekos_Lyseus/HRP",
    "https://fr.wiki.ryzom.com/wiki/Chapitre_IV_-_Guerrier_Sacr%C3%A9",
    "https://fr.wiki.ryzom.com/wiki/Chapitre_I_-_Le_Kami_Noir",
    "https://fr.wiki.ryzom.com/wiki/Chasseurs_disparus",
    "https://fr.wiki.ryzom.com/wiki/Chat",
    "https://fr.wiki.ryzom.com/wiki/Chercher_et_trouver",
    "https://fr.wiki.ryzom.com/wiki/Chiang_Le_Fort/HRP",
    "https://fr.wiki.ryzom.com/wiki/Utilisateur:Ciboulette",
    "https://fr.wiki.ryzom.com/wiki/Code_de_Conduite_de_Ryzom",
    "https://fr.wiki.ryzom.com/wiki/Comm_Marketing",
    "https://fr.wiki.ryzom.com/wiki/Commandes_sp%C3%A9ciales",
    "https://fr.wiki.ryzom.com/wiki/Comment_Cr%C3%A9er_une_page_Avatar",
    "https://fr.wiki.ryzom.com/wiki/Comment_Cr%C3%A9er_une_page_Guilde",
    "https://fr.wiki.ryzom.com/wiki/Comment_ins%C3%A9rer_la_Lore",
    "https://fr.wiki.ryzom.com/wiki/Comment_voir_facilement_un_.shape_en_jeu",
    "https://fr.wiki.ryzom.com/wiki/Commerce/Archives",
    "https://fr.wiki.ryzom.com/wiki/Communaut%C3%A9",
    "https://fr.wiki.ryzom.com/wiki/Communiqu%C3%A9_de_presse_2016_04_15",
    "https://fr.wiki.ryzom.com/wiki/Concours",
    "https://fr.wiki.ryzom.com/wiki/Conseils_pour_jeunes_r%C3%A9fugi%C3%A9s",
    "https://fr.wiki.ryzom.com/wiki/Contr%C3%B4les_de_l%27interface_utilisateur/Les_affichages_de_la_barre_des_t%C3%A2ches",
    "https://fr.wiki.ryzom.com/wiki/Conventions_Patches_%26_Updates",
    "https://fr.wiki.ryzom.com/wiki/Convoi_de_Crevette",
    "https://fr.wiki.ryzom.com/wiki/Copies_d%27%C3%A9cran_officielles",
    "https://fr.wiki.ryzom.com/wiki/Cours_",
    "https://fr.wiki.ryzom.com/wiki/Creenshaw",
    "https://fr.wiki.ryzom.com/wiki/Cr%C3%A9ation_de_Cat%C3%A9gorie:Lumi%C3%A8re_sur/GBA",
    "https://fr.wiki.ryzom.com/wiki/Cr%C3%A9ation_de_Lumi%C3%A8re_sur/Races/Semaine/6",
    "https://fr.wiki.ryzom.com/wiki/Customer_Support_Representative",
    "https://fr.wiki.ryzom.com/wiki/Dante_le_Taquin/HRP",
    "https://fr.wiki.ryzom.com/wiki/DeepL",
    "https://fr.wiki.ryzom.com/wiki/Diplomatie_Fyros_en_profondeur",
    "https://fr.wiki.ryzom.com/wiki/Discussion",
    "https://fr.wiki.ryzom.com/wiki/Editeur_sc%C3%A9nographique",
    "https://fr.wiki.ryzom.com/wiki/Elyps",
    "https://fr.wiki.ryzom.com/wiki/Emotes",
    "https://fr.wiki.ryzom.com/wiki/EncyclopAtys",
    "https://fr.wiki.ryzom.com/wiki/Encyclop%C3%A9die",
    "https://fr.wiki.ryzom.com/wiki/Event_Team",
    "https://fr.wiki.ryzom.com/wiki/Ev%C3%A9nement_2600",
    "https://fr.wiki.ryzom.com/wiki/Exemple_langage",
    "https://fr.wiki.ryzom.com/wiki/Exemples_d%27appartements",
    "https://fr.wiki.ryzom.com/wiki/Exporter_depuis_3DSMax",
    "https://fr.wiki.ryzom.com/wiki/Faire_un_feu_de_camp",
    "https://fr.wiki.ryzom.com/wiki/Feu_Sacr%C3%A9",
    "https://fr.wiki.ryzom.com/wiki/Forge_",
    "https://fr.wiki.ryzom.com/wiki/Format_de_fichiers",
    "https://fr.wiki.ryzom.com/wiki/Fyros",
    "https://fr.wiki.ryzom.com/wiki/Fyrk_lexique_test",
    "https://fr.wiki.ryzom.com/wiki/F%C3%AAte_de_la_libert%C3%A9",
    "https://fr.wiki.ryzom.com/wiki/F%C3%AAte_des_r%C3%A9fugi%C3%A9s/",
    "https://fr.wiki.ryzom.com/wiki/GBA_",
    "https://fr.wiki.ryzom.com/wiki/Gazette_du_d%C3%A9sert/",
    "https://fr.wiki.ryzom.com/wiki/Gestion_lumi%C3%A8re_sur_fauna",
    "https://fr.wiki.ryzom.com/wiki/Gestion_lumi%C3%A8re_sur_flora",
    "https://fr.wiki.ryzom.com/wiki/Gnostes%E2%88%B4Tenants/HRP",
    "https://fr.wiki.ryzom.com/wiki/Gubani_tr%C3%A8s_fortun%C3%A9",
    "https://fr.wiki.ryzom.com/wiki/Guide_Easy_Dapper",
    "https://fr.wiki.ryzom.com/wiki/Guide_Technique_du_wiki",
    "https://fr.wiki.ryzom.com/wiki/Guide_de_r%C3%A9daction",
    "https://fr.wiki.ryzom.com/wiki/Guides_d%27artisanat_d%27Arcueid",
    "https://fr.wiki.ryzom.com/wiki/Guilde/",
    "https://fr.wiki.ryzom.com/wiki/Help_contents",
    "https://fr.wiki.ryzom.com/wiki/How_to_Zanata.org",
    "https://fr.wiki.ryzom.com/wiki/Http://en.wiki.ryzom.com/wiki/New2017",
    "https://fr.wiki.ryzom.com/wiki/IRC",
    "https://fr.wiki.ryzom.com/wiki/Id%C3%A9es",
    "https://fr.wiki.ryzom.com/wiki/Id%C3%A9es_de_pi%C3%A8ces_de_th%C3%A9%C3%A2tre",
    "https://fr.wiki.ryzom.com/wiki/Indicateurs_des_inventaires",
    "https://fr.wiki.ryzom.com/wiki/Infographie",
    "https://fr.wiki.ryzom.com/wiki/Installer_Ryzom",
    "https://fr.wiki.ryzom.com/wiki/Journal_de_Ciboulette_",
    "https://fr.wiki.ryzom.com/wiki/Justice_zora%C3%AF/HRP",
    "https://fr.wiki.ryzom.com/wiki/KK",
    "https://fr.wiki.ryzom.com/wiki/K_Start_Tst",
    "https://fr.wiki.ryzom.com/wiki/Kitins_des_profondeurs/HRP",
    "https://fr.wiki.ryzom.com/wiki/L%27%C3%A9quipe_d%27animation",
    "https://fr.wiki.ryzom.com/wiki/LPOLTF_Dossier",
    "https://fr.wiki.ryzom.com/wiki/L_",
    "https://fr.wiki.ryzom.com/wiki/La_chute_de_Pyr",
    "https://fr.wiki.ryzom.com/wiki/La_cit%C3%A9_l%C3%A9gendaire_de_Sokkaria",
    "https://fr.wiki.ryzom.com/wiki/Le_Livre_du_SKA",
    "https://fr.wiki.ryzom.com/wiki/League",
    "https://fr.wiki.ryzom.com/wiki/Les_H%C3%B4tes_des_cit%C3%A9s",
    "https://fr.wiki.ryzom.com/wiki/Les_macros/avec_emotes",
    "https://fr.wiki.ryzom.com/wiki/Les_qu%C3%AAtes_des_quatre_Sages",
    "https://fr.wiki.ryzom.com/wiki/Les_%C2%ABBoss%C2%BB_maraudeurs",
    "https://fr.wiki.ryzom.com/wiki/Level-Design",
    "https://fr.wiki.ryzom.com/wiki/Liste_des_emplacements_perso",
    "https://fr.wiki.ryzom.com/wiki/Liste_des_objets_%C3%A9quipables", # TO KEEP ?
    "https://fr.wiki.ryzom.com/wiki/Liste_des_serveurs",
    "https://fr.wiki.ryzom.com/wiki/Livraison",
    "https://fr.wiki.ryzom.com/wiki/Lixie_la_Furie/HRP",
    "https://fr.wiki.ryzom.com/wiki/Lore",
    "https://fr.wiki.ryzom.com/wiki/Lore:Essai_de_lore_centralis%C3%A9e",
    "https://fr.wiki.ryzom.com/wiki/Loristes",
    "https://fr.wiki.ryzom.com/wiki/Lumi%C3%A8re_sur/",
    "https://fr.wiki.ryzom.com/wiki/L%E2%80%99%C3%A9tude_des_symboles_ou_la_symbologie",
    "https://fr.wiki.ryzom.com/wiki/MP",
    "https://fr.wiki.ryzom.com/wiki/Macro",
    "https://fr.wiki.ryzom.com/wiki/Manuel_de_",
    "https://fr.wiki.ryzom.com/wiki/Maraudeurs",
    "https://fr.wiki.ryzom.com/wiki/Marchand",
    "https://fr.wiki.ryzom.com/wiki/March%C3%A9_de_la_Cit%C3%A9_d%27Avalae",
    "https://fr.wiki.ryzom.com/wiki/March%C3%A9_de_Zachini(Alternatys)",
    "https://fr.wiki.ryzom.com/wiki/Mariage_de_Kyriann_et_Ostium/Lucios",
    "https://fr.wiki.ryzom.com/wiki/Matis",
    "https://fr.wiki.ryzom.com/wiki/Mauvaise_influence",
    "https://fr.wiki.ryzom.com/wiki/Mercenaires_%C3%89carlates/HRP",
    "https://fr.wiki.ryzom.com/wiki/Mission",
    "https://fr.wiki.ryzom.com/wiki/Modif_de_sys_info/client",
    "https://fr.wiki.ryzom.com/wiki/Modifications_graphique",
    "https://fr.wiki.ryzom.com/wiki/Mod%C3%A8le_de_sous_onglets_pour_le_fyros",
    "https://fr.wiki.ryzom.com/wiki/Mod%C3%A8le_portail",
    "https://fr.wiki.ryzom.com/wiki/Monture_invisible",
    "https://fr.wiki.ryzom.com/wiki/M%C3%A9tiers",
    "https://fr.wiki.ryzom.com/wiki/NASA-meetings",
    "https://fr.wiki.ryzom.com/wiki/Nettoyage_du_D%C3%A9sert/",
    "https://fr.wiki.ryzom.com/wiki/Nevrax",
    "https://fr.wiki.ryzom.com/wiki/NewForge",
    "https://fr.wiki.ryzom.com/wiki/New_Zone",
    "https://fr.wiki.ryzom.com/wiki/Nomm%C3%A9s_et_Rois",
    "https://fr.wiki.ryzom.com/wiki/Nomm%C3%A9s_et_Rois/Liste_par_r%C3%A9gion",
    "https://fr.wiki.ryzom.com/wiki/Nommer_ses_Templates",
    "https://fr.wiki.ryzom.com/wiki/Notes_population",
    "https://fr.wiki.ryzom.com/wiki/Nouveau_service_de_facturation",
    "https://fr.wiki.ryzom.com/wiki/Nouveaut%C3%A9s_",
    "https://fr.wiki.ryzom.com/wiki/Nuit_sur_l%27Ab%C3%AEme_du_D%C3%A9mon/",
    "https://fr.wiki.ryzom.com/wiki/Objet_prehensible",
    "https://fr.wiki.ryzom.com/wiki/Official_Lore_Template",
    "https://fr.wiki.ryzom.com/wiki/Orphie_Dradius/Les_fun%C3%A9railles_d%27Orphie/Les_Rangers",
    "https://fr.wiki.ryzom.com/wiki/Orphie_Dradius/Les_fun%C3%A9railles_d%27Orphie/Les_Amis",
    "https://fr.wiki.ryzom.com/wiki/Ouverture_au_public_de_l%E2%80%99EncyclopAtys_!",
    "https://fr.wiki.ryzom.com/wiki/PVP",
    "https://fr.wiki.ryzom.com/wiki/PVE",
    "https://fr.wiki.ryzom.com/wiki/PageType:PNJ",
    "https://fr.wiki.ryzom.com/wiki/Page_test_navigation_team",
    "https://fr.wiki.ryzom.com/wiki/PagesVides",
    "https://fr.wiki.ryzom.com/wiki/Palette_des_couleurs_sur_Atys",
    "https://fr.wiki.ryzom.com/wiki/Panoramas",
    "https://fr.wiki.ryzom.com/wiki/Patch",
    "https://fr.wiki.ryzom.com/wiki/Pei-Ruz_le_putr%C3%A9fi%C3%A9/HRP",
    "https://fr.wiki.ryzom.com/wiki/Pioche",
    "https://fr.wiki.ryzom.com/wiki/Poches",
    "https://fr.wiki.ryzom.com/wiki/Pocket_Worlds",
    "https://fr.wiki.ryzom.com/wiki/Portail_Arcanes/",
    "https://fr.wiki.ryzom.com/wiki/Portail_",
    "https://fr.wiki.ryzom.com/wiki/Pour_Atys_avec_reconnaissance",
    "https://fr.wiki.ryzom.com/wiki/Premier_Atyso%C3%ABl_dans_les_Nouvelles_Terres",
    "https://fr.wiki.ryzom.com/wiki/Projet_BugsHunter",
    "https://fr.wiki.ryzom.com/wiki/Projet_Id%C3%A9es",
    "https://fr.wiki.ryzom.com/wiki/Projet_d'Event",
    "https://fr.wiki.ryzom.com/wiki/Proto_2525",
    "https://fr.wiki.ryzom.com/wiki/Prototype",
    "https://fr.wiki.ryzom.com/wiki/Pr%C3%A9sentation_des_Webapps",
    "https://fr.wiki.ryzom.com/wiki/Puzzle",
    "https://fr.wiki.ryzom.com/wiki/Quand_DeepL_est_drole",
    "https://fr.wiki.ryzom.com/wiki/Quoi_de_neuf",
    "https://fr.wiki.ryzom.com/wiki/RC",
    "https://fr.wiki.ryzom.com/wiki/RG_LHMagic",
    "https://fr.wiki.ryzom.com/wiki/RP_G%C3%A9n%C3%A9ralit%C3%A9s",
    "https://fr.wiki.ryzom.com/wiki/RSS",
    "https://fr.wiki.ryzom.com/wiki/Raid_sur_Desertstock_2626",
    "https://fr.wiki.ryzom.com/wiki/Rangers",
    "https://fr.wiki.ryzom.com/wiki/Rcdsdfn",
    "https://fr.wiki.ryzom.com/wiki/Rcdstyp",
    "https://fr.wiki.ryzom.com/wiki/Rcskillcodes",
    "https://fr.wiki.ryzom.com/wiki/Rcticks",
    "https://fr.wiki.ryzom.com/wiki/Recrutement",
    "https://fr.wiki.ryzom.com/wiki/Renomm%C3%A9e",
    "https://fr.wiki.ryzom.com/wiki/Rendor/Chronique",
    "https://fr.wiki.ryzom.com/wiki/Reportages",
    "https://fr.wiki.ryzom.com/wiki/Rg_Sceau_de_la_Reine",
    "https://fr.wiki.ryzom.com/wiki/Rigolades",
    "https://fr.wiki.ryzom.com/wiki/Roue_de_la_Fortune",
    "https://fr.wiki.ryzom.com/wiki/Route_de_l'Eau_de_2624/",
    "https://fr.wiki.ryzom.com/wiki/Rumeurs",
    "https://fr.wiki.ryzom.com/wiki/RyZtart",
    "https://fr.wiki.ryzom.com/wiki/Rywards",
    "https://fr.wiki.ryzom.com/wiki/Ryzom",
    "https://fr.wiki.ryzom.com/wiki/R%C3%A9cap_des_portails",
    "https://fr.wiki.ryzom.com/wiki/R%C3%A9cap_des_tribus",
    "https://fr.wiki.ryzom.com/wiki/R%C3%A9union_de_la_guilde_d%27Elias,_Fairhaven",
    "https://fr.wiki.ryzom.com/wiki/SN",
    "https://fr.wiki.ryzom.com/wiki/SOS",
    "https://fr.wiki.ryzom.com/wiki/Saltorn",
    "https://fr.wiki.ryzom.com/wiki/Saucyzon",
    "https://fr.wiki.ryzom.com/wiki/Second_Essaim/HRP",
    "https://fr.wiki.ryzom.com/wiki/Sentier_des_Torbaks",
    "https://fr.wiki.ryzom.com/wiki/Serveurs",
    "https://fr.wiki.ryzom.com/wiki/Shard",
    "https://fr.wiki.ryzom.com/wiki/Signaler_un_Bogue",
    "https://fr.wiki.ryzom.com/wiki/Silan/Guide_du_refugie_a_Silan",
    "https://fr.wiki.ryzom.com/wiki/Sirgio_le_Sc%C3%A9l%C3%A9rat/HRP",
    "https://fr.wiki.ryzom.com/wiki/Sitem.dfn",
    "https://fr.wiki.ryzom.com/wiki/Songe_d%27une_nuit_d%27hiver/logs",
    "https://fr.wiki.ryzom.com/wiki/Spectacle_de_rue",
    "https://fr.wiki.ryzom.com/wiki/Spoiler_et_HRP_dans_le_wiki",
    "https://fr.wiki.ryzom.com/wiki/Storyline",
    "https://fr.wiki.ryzom.com/wiki/Support",
    "https://fr.wiki.ryzom.com/wiki/TJ_L%27Esprit_de_No%C3%ABl",
    "https://fr.wiki.ryzom.com/wiki/Tableau_des_ennemis",
    "https://fr.wiki.ryzom.com/wiki/Tags_PvP_Roleplay",
    "https://fr.wiki.ryzom.com/wiki/Tags_RP",
    "https://fr.wiki.ryzom.com/wiki/Tannick/Galerie",
    "https://fr.wiki.ryzom.com/wiki/Tarte_pour_Mar-Ni",
    "https://fr.wiki.ryzom.com/wiki/Team_Administration_List",
    "https://fr.wiki.ryzom.com/wiki/Teeneemai",
    "https://fr.wiki.ryzom.com/wiki/Template_langage",
    "https://fr.wiki.ryzom.com/wiki/Test",
    "https://fr.wiki.ryzom.com/wiki/Textures_environnementales",
    "https://fr.wiki.ryzom.com/wiki/Thanksgiving",
    "https://fr.wiki.ryzom.com/wiki/The_Saga_of_Ryzom",
    "https://fr.wiki.ryzom.com/wiki/Th%C3%A9matique",
    "https://fr.wiki.ryzom.com/wiki/Titres",
    "https://fr.wiki.ryzom.com/wiki/Tournoi_de_l%27%C3%AEle",
    "https://fr.wiki.ryzom.com/wiki/Translation",
    "https://fr.wiki.ryzom.com/wiki/Transporter",
    "https://fr.wiki.ryzom.com/wiki/Trucs_et_astuces_d%27int%C3%A9gration_de_la_Lore",
    "https://fr.wiki.ryzom.com/wiki/Tunnel_des_Malheurs/Analyse_topographique_JA_2610",
    "https://fr.wiki.ryzom.com/wiki/Tutori",
    "https://fr.wiki.ryzom.com/wiki/Tynasus_XIV_l%27Extravagant",
    "https://fr.wiki.ryzom.com/wiki/T%C3%A9l%C3%A9porteur_",
    "https://fr.wiki.ryzom.com/wiki/Trykers",
    "https://fr.wiki.ryzom.com/wiki/Uchronie_",
    "https://fr.wiki.ryzom.com/wiki/UnePageRPetHRP",
    "https://fr.wiki.ryzom.com/wiki/Une_ode_%C3%A0_vos_pieds",
    "https://fr.wiki.ryzom.com/wiki/Une_vieille_archive/Assembl%C3%A9e_Ranger_du_Holeth,_Folially_18,_4e_CA_2609",
    "https://fr.wiki.ryzom.com/wiki/Utiliser_la_carte",
    "https://fr.wiki.ryzom.com/wiki/Vague_blanche",
    "https://fr.wiki.ryzom.com/wiki/Veill%C3%A9e_des_contes_",
    "https://fr.wiki.ryzom.com/wiki/Vive_la_bi%C3%A8re",
    "https://fr.wiki.ryzom.com/wiki/Vue_d%27ensemble_des_Tribus/Table",
    "https://fr.wiki.ryzom.com/wiki/WIP:Chroniques",
    "https://fr.wiki.ryzom.com/wiki/WebIG",
    "https://fr.wiki.ryzom.com/wiki/Wiki_",
    "https://fr.wiki.ryzom.com/wiki/XY",
    "https://fr.wiki.ryzom.com/wiki/Xinqian/HRP",
    "https://fr.wiki.ryzom.com/wiki/Xymus_Tindix/HRP",
    "https://fr.wiki.ryzom.com/wiki/Yento",
    "https://fr.wiki.ryzom.com/wiki/Zanata.org",
    "https://fr.wiki.ryzom.com/wiki/Zig",
    "https://fr.wiki.ryzom.com/wiki/Zora%C3%AFs",
    "https://fr.wiki.ryzom.com/wiki/%C3%89lection_miss_mister_Atys",
    "https://fr.wiki.ryzom.com/wiki/%C3%89v%C3%A9nements_dynamiques"
]

EXTRA_URL_TO_SCRAP = [
    "https://fr.wiki.ryzom.com/wiki/Portail:Zora%C3%AF",
    "https://fr.wiki.ryzom.com/wiki/Portail:Zora%C3%AF/Histoire",
    "https://fr.wiki.ryzom.com/wiki/Portail:Zora%C3%AF/2525",
    "https://fr.wiki.ryzom.com/wiki/Portail:Zora%C3%AF/Protagonistes",
    "https://fr.wiki.ryzom.com/wiki/Portail:Zora%C3%AF/Relations",
    "https://fr.wiki.ryzom.com/wiki/Portail:Zora%C3%AF/Langage",
    "https://fr.wiki.ryzom.com/wiki/Portail:Matis",
    "https://fr.wiki.ryzom.com/wiki/Portail:Matis/Histoire",
    "https://fr.wiki.ryzom.com/wiki/Portail:Matis/2525",
    "https://fr.wiki.ryzom.com/wiki/Portail:Matis/Protagonistes",
    "https://fr.wiki.ryzom.com/wiki/Portail:Matis/Relations",
    "https://fr.wiki.ryzom.com/wiki/Portail:Matis/Mateis",
    "https://fr.wiki.ryzom.com/wiki/Portail:Matis/Mateis/Mateis_Classique",
    "https://fr.wiki.ryzom.com/wiki/Portail:Fyros",
    "https://fr.wiki.ryzom.com/wiki/Portail:Fyros/Histoire",
    "https://fr.wiki.ryzom.com/wiki/Portail:Fyros/2525",
    "https://fr.wiki.ryzom.com/wiki/Portail:Fyros/Protagonistes",
    "https://fr.wiki.ryzom.com/wiki/Portail:Fyros/Relations",
    "https://fr.wiki.ryzom.com/wiki/Portail:Fyros/fyrk",
    "https://fr.wiki.ryzom.com/wiki/Portail:Fyros/fyrk/lexique",
    "https://fr.wiki.ryzom.com/wiki/Portail:Tryker",
    "https://fr.wiki.ryzom.com/wiki/Portail:Tryker/Histoire",
    "https://fr.wiki.ryzom.com/wiki/Portail:Tryker/2525",
    "https://fr.wiki.ryzom.com/wiki/Portail:Tryker/Protagonistes",
    "https://fr.wiki.ryzom.com/wiki/Portail:Tryker/Relations",
    "https://fr.wiki.ryzom.com/wiki/Portail:Tryker/Langage",
    "https://fr.wiki.ryzom.com/wiki/Portail:Tryker/Langage/Grammaire_tryker",
    "https://fr.wiki.ryzom.com/wiki/Portail:Maraudeurs",
    "https://fr.wiki.ryzom.com/wiki/Portail:Maraudeurs/Histoire",
    "https://fr.wiki.ryzom.com/wiki/Portail:Maraudeurs/Protagonistes",
    "https://fr.wiki.ryzom.com/wiki/Portail:Maraudeurs/Relations",
    "https://fr.wiki.ryzom.com/wiki/Portail:Maraudeurs/Langage",
    "https://fr.wiki.ryzom.com/wiki/Portail:Maraudeurs/Marund/Lexique",
    "https://fr.wiki.ryzom.com/wiki/Portail:Rangers",
    "https://fr.wiki.ryzom.com/wiki/Portail:Rangers/Protagonistes",
    "https://fr.wiki.ryzom.com/wiki/Portail:Rangers/Langage",
    "https://fr.wiki.ryzom.com/wiki/Portail:Trytonistes/Protagonistes"
]
