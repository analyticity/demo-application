from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class AccidentsAttributes(BaseModel):
    id_nehody: int
    datum: Optional[datetime] = None
    cas: Optional[str] = None
    kraj: Optional[str] = None
    okres: Optional[str] = None
    lokalita: Optional[str] = None
    druh_nehody: Optional[str] = None
    druh_srazky_vozidel: Optional[str] = None
    prekazka: Optional[str] = None
    druh_zvirete: Optional[str] = None
    charakter: Optional[str] = None
    zavineni: Optional[str] = None
    alkohol: Optional[str] = None
    drogy: Optional[str] = None
    hlavni_pricina: Optional[str] = None
    usmrceno_osob: Optional[int] = None
    tezce_zraneno_osob: Optional[int] = None
    lehce_zraneno_osob: Optional[int] = None
    celkova_skoda: Optional[int] = None
    # druh_povrchu_voz: Optional[str] = None
    stav_povrchu_voz: Optional[str] = None
    stav_vozovky: Optional[str] = None
    povetrnostni_podm: Optional[str] = None
    viditelnost: Optional[str] = None
    rozhled: Optional[str] = None
    deleni_komun: Optional[str] = None
    situovani: Optional[str] = None
    rizeni_provozu_v_dobe_nehody: Optional[str] = None
    mistni_uprava_prednosti_v_jizde: Optional[str] = None
    #specificka_mista_a_objekty_v_miste_nehody: Optional[str | int] = None
    smerove_pomery: Optional[str] = None
    kategorie_chodce: Optional[str] = None
    reflexni_prvky_u_chodce: Optional[str] = None
    chodec_na_osobnim_prepravniku: Optional[str] = None
    stav_chodce: Optional[str] = None
    alkohol_u_chodce_pritomen: Optional[str] = None
    druh_drogy_u_chodce: Optional[str] = None
    pocet_vozidel: Optional[int] = None
    misto_nehody: Optional[str] = None
    druh_komun: Optional[str] = None
    cislo_pozemni_komunikace: Optional[str] = None
    druh_krizujici_komunikace: Optional[str] = None
    druh_vozidla: Optional[str] = None
    vyrobni_znacka_motoroveho_vozidla: Optional[str] = None
    rok_vyroby_vozidla: Optional[str] = None
    charakteristika_vozidla: Optional[str] = None
    smyk: Optional[str] = None
    vozidlo_po_nehode: Optional[str] = None
    unik_provoznich_prepravovanych_hmot: Optional[str] = None
    zpusob_vyprosteni_osob_z_vozidla: Optional[str] = None
    smer_jizdy_nebo_postaveni_vozidla: Optional[str] = None
    kategorie_ridice: Optional[str] = None
    stav_ridice: Optional[str] = None
    vnejsi_ovlivneni_ridice: Optional[str] = None
    nasledky: Optional[str] = None

    @field_validator("datum", mode="before")
    def validate_date(cls, value):
        return datetime.strptime(value, "%d/%m/%Y")

    @field_validator("cas", mode="before")
    def validate_time(cls, value):
        if not value:
            return None
        
        value = str(value).replace('.0', '')
        
        value = value.zfill(4)
        
        try:
            hours, minutes = int(value[:-2]), int(value[-2:])
            
            if minutes >= 60:
                return None
            
            return f"{hours:02d}:{minutes:02d}"
        except ValueError:
            return None
