import os
from dotenv import load_dotenv

load_dotenv()

class storage:
    """Class that only contains constant 
    (ex. Discord Token and my youtube-dl download option)
    """
    TOKEN: str = os.getenv('DISCORD_TOKEN')
    GINO_ID: int = int(os.getenv('GINO'))

    offese: list = (
        " ha bisogno di un nuovo buco del culo",
        " ha il cazzo storto",
        " non si lava da due anni",
        " piace essere picchiato con delle mazze chiodate",
        " vuole essere sodomizzato",
        " tua madre è come la doccia, me la faccio tutti i giorni.",
        " hai così poca materia cerebrale che galleggi in acqua.",
        " non ti insulto perchè poi dovrei spiegartelo in seguito quindi lascia perdere.",
        " non sai nulla. Scusa, sai meno di nulla, perchè se sapessi di non sapere nulla sarebbe qualcosa.",
        " sei così brutto che non troveresti una prostituta nei giorni di sconto.",
        " sai che hai proprio un bel viso, ti cerco un colloquio per lavorare in radio.",
        " il tuo ano è geloso della tua bocca da quanta merda esce da quella fogna.",
        " se io fossi cieco, sordo e disperato non ti chiaverei ugualmente.",
        " mi dai così fastidio che per farti sta zitto ti farei inculare da dei negri sordi, così quando dici basta non ti sentono.",
        " si scopa le obese",
        " sei un grimaldello nello culo che rotea",
        " lecca le orecchie di un maiale in una macelleria cinese abusiva",
        " hai il cazzo così piccoli che se guardi in bassa vedi solo la pancia",
        " capisci la metà di uno che non ne capisce un cazzo",
        " usa i tarzanelli per aromatizzare la tua acqua di colonia",
        " si mette 3 dita in culo e gode",
        " vota il movimento 5 stelle",
        " sputa in culo ai gatti",
        " fa un elicottero sincronizzato con un ventilatore.",
        " sarebbe bello se avessi anche neuroni",
        " ti è caduto il cervello nelle tette?",
        " segue mate",
        " esplodi, con affetto.",
        " sei un pollo.",
        " sei così coglione che non capisci la differenza della S fra rosa e sonno.",
        " sei come Cuoghi, un incompetente puttana.",
        " ha il cazzo a uncinetto",
        " sei così tardo che per rispondere all’appello dici: prof mi sente?",
    )

    ydl_opts = {
        'format': '249/250/251',
        'logtostderr': False,
        'quiet': True,
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    }