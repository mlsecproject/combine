import ConfigParser
import bs4
import datetime
import feedparser
import json
import re
from logger import get_logger
from csv import reader
from itertools import ifilter

logger = get_logger('thresher')


def indicator_type(indicator):
    ip_regex = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    domain_regex = r'(www\.)?(?P<address>([\d\w.][-\d\w.]{0,253}[\d\w.]+\.)+(xn--vermgensberatung-pwb|xn--vermgensberater-ctb|xn--clchc0ea0b2g2a9gcd|xn--xkc2dl3a5ee0h|xn--mgberp4a5d4ar|xn--xkc2al3hye2a|xn--nqv7fs00ema|xn--mgbc0a9azcg|xn--mgba3a4f16a|xn--lgbbat1ad8j|xn--i1b6b1a6a2e|xn--mgbx4cd0ab|xn--mgbbh1a71e|xn--mgbayh7gpa|xn--mgbaam7a8h|xn--fiq228c5hs|xn--b4w605ferd|xn--6qq986b3xl|cancerresearch|xn--ygbi2ammx|xn--yfro4i67o|xn--fzc2c9e2c|xn--fpcrj9c3d|spreadbetting|international|xn--qcka1pmc|xn--ogbpf8fl|xn--ngbc5azd|xn--mgbab2bd|xn--mgb9awbf|xn--80asehdb|xn--80adxhks|xn--3e0b707e|versicherung|construction|xn--zfr164b|xn--xhq521b|xn--vuq861b|xn--ses554g|xn--s9brj9c|xn--rhqv96g|xn--q9jyb4c|xn--pgbs0dh|xn--kpry57d|xn--kprw13d|xn--j6w193g|xn--hxt814e|xn--h2brj9c|xn--gecrj9c|xn--flw351e|xn--d1acj3b|xn--czr694b|xn--80ao21a|xn--6frz82g|xn--55qw42g|xn--45brj9c|xn--3ds443g|xn--3bst00m|xn--1qqw23a|williamhill|productions|photography|motorcycles|investments|enterprises|engineering|contractors|blackfriday|barclaycard|accountants|xn--wgbl6a|xn--wgbh1c|xn--unup4y|xn--o3cw4h|xn--mxtq1m|xn--kput3i|xn--io0a7i|xn--fiqz9s|xn--fiqs8s|xn--fiq64b|xn--czru2d|xn--czrs0t|xn--cg4bki|xn--9et52u|xn--90a3ac|xn--80aswg|xn--55qx5d|xn--4gbrim|xn--45q11c|xn--30rr7y|vlaanderen|university|technology|restaurant|republican|properties|management|industries|immobilien|healthcare|foundation|eurovision|cuisinella|creditcard|consulting|bnpparibas|associates|apartments|accountant|yodobashi|xn--vhquv|xn--p1acf|xn--nqv7f|xn--l1acc|xn--j1amh|xn--d1alf|xn--c1avg|xn--90ais|vacations|solutions|melbourne|marketing|institute|goldpoint|furniture|financial|equipment|education|directory|community|christmas|bloomberg|aquarelle|amsterdam|allfinanz|yokohama|xn--p1ai|xn--node|ventures|training|supplies|software|services|saarland|redstone|property|plumbing|pictures|pharmacy|partners|mortgage|memorial|marriott|lighting|infiniti|holdings|graphics|football|flsmidth|firmdale|feedback|exchange|everbank|engineer|download|discount|diamonds|democrat|delivery|computer|clothing|cleaning|catering|capetown|business|builders|budapest|brussels|boutique|bargains|barclays|attorney|airforce|zuerich|youtube|whoswho|wedding|website|trading|toshiba|tickets|temasek|systems|surgery|support|spiegel|singles|shriram|shiksha|science|schwarz|schmidt|samsung|reviews|rentals|recipes|realtor|panerai|organic|okinawa|neustar|network|markets|limited|leclerc|latrobe|lacaixa|komatsu|kitchen|hosting|holiday|hangout|hamburg|guitars|gallery|frogans|forsale|flowers|florist|flights|fitness|fishing|finance|fashion|exposed|domains|digital|dentist|cruises|cricket|courses|country|cooking|company|cologne|college|channel|cartier|careers|caravan|capital|auction|android|academy|abogado|yandex|yachts|webcam|voyage|voting|vision|villas|viajes|travel|tienda|tennis|tattoo|taipei|sydney|suzuki|supply|social|schule|school|ryukyu|review|report|repair|reisen|quebec|pictet|piaget|physio|photos|otsuka|oracle|online|nissan|nagoya|museum|moscow|mormon|monash|market|maison|madrid|luxury|london|lawyer|kaufen|juegos|joburg|insure|hiphop|hermes|gratis|google|global|garden|futbol|expert|events|estate|energy|emerck|durban|doosan|direct|design|dental|degree|datsun|dating|credit|condos|coffee|clinic|claims|church|chrome|center|casino|career|camera|berlin|bayern|alsace|agency|active|abbott|world|works|watch|wales|vodka|video|vegas|trust|trade|tours|tools|tokyo|today|tirol|tires|tatar|sucks|style|study|space|solar|shoes|rodeo|rocks|reise|rehab|press|praxi|poker|place|pizza|photo|party|parts|paris|osaka|ninja|nexus|movie|money|miami|media|mango|lotto|lotte|loans|legal|lease|kyoto|koeln|jetzt|irish|house|horse|homes|guide|gripe|green|gmail|globo|glass|gives|gifts|forex|faith|epson|email|deals|dance|dabur|cymru|codes|coach|click|citic|chloe|cheap|cards|canon|build|boats|black|bingo|autos|audio|archi|adult|actor|zone|yoga|work|wiki|wien|wang|voto|vote|toys|town|tips|tech|surf|sohu|site|sexy|scot|saxo|sarl|sale|ruhr|rsvp|rich|rest|reit|qpon|prof|prod|post|porn|pohl|plus|pink|pics|page|nico|news|navy|name|mtpc|moda|mobi|mini|menu|meme|meet|maif|luxe|ltda|loan|link|limo|life|lidl|lgbt|land|kred|kiwi|kddi|jobs|java|info|immo|host|here|help|haus|guru|guge|goog|golf|gold|gift|ggee|gent|gbiz|fund|fish|film|farm|fans|fail|erni|dvag|doha|docs|diet|desi|dclk|date|coop|cool|club|city|chat|cern|cash|casa|care|camp|buzz|bond|blue|bike|best|beer|bank|band|asia|arpa|army|aero|zip|xyz|xxx|xin|wtf|wtc|wme|win|wed|vet|uol|uno|tui|top|tel|tax|soy|sky|sew|scb|sca|sap|rip|rio|ren|red|pub|pro|ovh|org|ooo|onl|ong|one|nyc|ntt|nrw|nra|nhk|ngo|new|net|mtn|mov|moe|mma|mil|lds|lat|krd|kim|jcb|iwc|int|ink|ing|ifm|ibm|how|hiv|gov|gop|goo|gmx|gmo|gle|gdn|gal|frl|foo|fly|fit|fan|eus|esq|edu|eat|dnp|dev|day|dad|crs|com|cfd|ceo|cbn|cat|cal|cab|bzh|boo|bmw|biz|bio|bid|bbc|bar|axa|afl|ads|zw|zm|za|yt|ye|ws|wf|vu|vn|vi|vg|ve|vc|va|uz|uy|us|uk|ug|ua|tz|tw|tv|tt|tr|to|tn|tm|tl|tk|tj|th|tg|tf|td|tc|sz|sy|sx|sv|su|st|sr|so|sn|sm|sl|sk|sj|si|sh|sg|se|sd|sc|sb|sa|rw|ru|rs|ro|re|qa|py|pw|pt|ps|pr|pn|pm|pl|pk|ph|pg|pf|pe|pa|om|nz|nu|nr|np|no|nl|ni|ng|nf|ne|nc|na|mz|my|mx|mw|mv|mu|mt|ms|mr|mq|mp|mo|mn|mm|ml|mk|mh|mg|me|md|mc|ma|ly|lv|lu|lt|ls|lr|lk|li|lc|lb|la|kz|ky|kw|kr|kp|kn|km|ki|kh|kg|ke|jp|jo|jm|je|it|is|ir|iq|io|in|im|il|ie|id|hu|ht|hr|hn|hm|hk|gy|gw|gu|gt|gs|gr|gq|gp|gn|gm|gl|gi|gh|gg|gf|ge|gd|gb|ga|fr|fo|fm|fk|fj|fi|eu|et|es|er|eg|ee|ec|dz|do|dm|dk|dj|de|cz|cy|cx|cw|cv|cu|cr|co|cn|cm|cl|ck|ci|ch|cg|cf|cd|cc|ca|bz|by|bw|bv|bt|bs|br|bo|bn|bm|bj|bi|bh|bg|bf|be|bd|bb|ba|az|ax|aw|au|at|as|ar|aq|ao|an|am|al|ai|ag|af|ae|ad|ac))'

    if re.match(ip_regex, indicator):
        return "IPv4"
    elif re.match(domain_regex, indicator, re.IGNORECASE):
        return "FQDN"
    else:
        return None


def process_simple_list(response, source, direction):
    data = []
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', current_date))
    return data


def process_sans(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            # Because SANS zero-pads their addresses
            i = re.sub(r'\.0{1,2}', '.', line.split()[0].lstrip('0'))
            date = line.split()[-1]
            data.append((i, indicator_type(i), direction, source, '', date))
    return data


def process_virbl(response, source, direction):
    data = []
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('E') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', current_date))
    return data


def process_project_honeypot(response, source, direction):
    data = []
    for entry in feedparser.parse(response).entries:
        i = entry.title.partition(' ')[0]
        i_date = entry.description.split(' ')[-1]
        data.append((i, indicator_type(i), direction, source, '', i_date))
    return data


def process_drg(response, source, direction):
    data = []
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.split('|')[2].strip()
            data.append((i, indicator_type(i), direction, source, '', current_date))
    return data


def process_alienvault(response, source, direction):
    data = []
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition('#')[0].strip()
            note = line.split('#')[3].strip()
            if 'Scanning Host' in note or 'Spamming' in note:
                direction = 'inbound'
            elif 'Malware' in note or 'C&C' in note or 'APT' in note:
                direction = 'outbound'
            data.append((i, indicator_type(i), direction, source, note, current_date))
    return data


def process_rulez(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition('#')[0].strip()
            date = line.partition('#')[2].split(' ')[1]
            data.append((i, indicator_type(i), direction, source, '', date))
    return data


def process_packetmail(response, source, direction):
    data = []
    filter_comments = lambda x: not x[0].startswith('#')
    try:
        for line in ifilter(filter_comments,
                            reader(response.splitlines(), delimiter=';')):
            i = line[0]
            date = line[1].split(' ')[1]
            data.append((i, indicator_type(i), direction, source, '', date))
    except (IndexError, AttributeError):
        pass
    return data


def process_autoshun(response, source, direction):
    data = []
    if response.startswith("Couldn't select database"):
        return data
    for line in response.splitlines():
		# Fixed unauthenticated sites, please test accordingly
        if line.startswith("Please"):
            logger.info("Skipping site " + source)
            break
        elif not line.startswith('S') and len(line) > 0:
            i = line.partition(',')[0].strip()
            date = line.split(',')[1].split()[0]
            note = line.split(',')[-1]
            data.append((i, indicator_type(i), direction, source, note, date))
    return data


def process_haleys(response, source, direction):
    data = []
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition(':')[2].strip()
            data.append((i, indicator_type(i), direction, source, '', current_date))
    return data


def process_malwaregroup(response, source, direction):
    data = []
    soup = bs4.BeautifulSoup(response)
    for row in soup.find_all('tr'):
        if row.td:
            i = row.td.text
            date = row.contents[-1].text
            data.append((i, indicator_type(i), direction, source, '', date))
    return data


def thresh(input_file, output_file):

    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Thresher: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    logger.info('Loading raw feed data from %s', input_file)
    with open(input_file, 'rb') as f:
        crop = json.load(f)

    harvest = []
    # TODO: replace with a proper plugin system (cf. #23)
    thresher_map = {'blocklist.de': process_simple_list,
                    'openbl': process_simple_list,
                    'projecthoneypot': process_project_honeypot,
                    'ciarmy': process_simple_list,
                    'alienvault': process_alienvault,
                    'rulez': process_rulez,
                    'sans': process_sans,
                    'http://www.nothink.org/blacklist/blacklist_ssh': process_simple_list,
                    'http://www.nothink.org/blacklist/blacklist_malware': process_simple_list,
                    'abuse.ch': process_simple_list,
                    'packetmail': process_packetmail,
                    'autoshun': process_autoshun,
                    'the-haleys': process_haleys,
                    'virbl': process_simple_list,
                    'dragonresearchgroup': process_drg,
                    'malwaregroup': process_malwaregroup,
                    'malc0de': process_simple_list,
                    'file://': process_simple_list}

    # When we have plugins, this hack won't be necessary
    for response in crop['inbound']:
        logger.info('Evaluating %s', response[0])
        # TODO: logging
        if response[1] == 200:
            for site in thresher_map:
                if site in response[0]:
                    logger.info('Parsing feed from %s', response[0])
                    harvest += thresher_map[site](response[2], response[0], 'inbound')
                else:  # how to handle non-mapped sites?
                    pass
        else:  # how to handle non-200 non-404?
            logger.error('Could not handle %s: %s', response[0], response[1])

    for response in crop['outbound']:
        if response[1] == 200:
            for site in thresher_map:
                if site in response[0]:
                    logger.info('Parsing feed from %s', response[0])
                    harvest += thresher_map[site](response[2], response[0], 'outbound')
                else:  # how to handle non-mapped sites?
                    pass
        else:  # how to handle non-200 non-404?
            pass

    logger.info('Storing parsed data in %s', output_file)
    with open(output_file, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    thresh('harvest.json', 'crop.json')
