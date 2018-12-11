from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin
from flask_security.utils import encrypt_password
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('iq_update_config.py')
db = SQLAlchemy(app)

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class ServicePack(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(20), unique=True, nullable=False)
    version_number = db.Column(db.Integer(), unique=True, nullable=False)
    release_date = db.Column(db.Date(), nullable=False)

    def __str__(self):
        return "{} - {}".format(self.description, self.release_date)


class ServicePackDetail(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    language = db.Column(db.Enum('de', 'en'), nullable=False)
    contents = db.Column(db.Text, nullable=False)
    service_pack_id = db.Column(db.Integer, db.ForeignKey(ServicePack.id), nullable=False)
    service_pack = db.relation(ServicePack, backref='details')

    def __str__(self):
        return "{} - {}".format(self.language, self.contents)

    def __repr__(self):
        return self.__str__


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


def build_sample_db():
    db.drop_all()
    db.create_all()
    with app.app_context():
        if len(User.query.all()) == 0:
            release_user_role = Role(name='releaseuser')
            super_user_role = Role(name='superuser')
            db.session.add(release_user_role)
            db.session.add(super_user_role)
            db.session.add(
                User(first_name='Administrator', last_name='Apis', email='admin', password=encrypt_password('admin'),
                     active=True,
                     roles=[super_user_role]))
            db.session.add(
                User(first_name='ReleaseManager', last_name='Apis', email='release',
                     password=encrypt_password('release'), active=True,
                     roles=[release_user_role]))
            db.session.commit()
    if len(ServicePack.query.all()) == 0:
        description = 'Version 6.5 0161'
        version_number = int(description.split(' ')[-1])
        db.session.add(
            ServicePack(description=description, version_number=version_number,
                        release_date=datetime(2018, 11, 30, 23, 59, 59, 00)))
        sp = ServicePack.query.filter_by(version_number=version_number).first()
        db.session.add(ServicePackDetail(service_pack_id=sp.id, language='de',
                                         contents='<p><B><U>Allgemein:</U></B></p><UL><li> RP-5381: '
                                                  'Varianten-Matrix-Editor: Die Darstellung der Objekt-Bezeichnungen '
                                                  'in den Zeilen bzw. Spalten waren teilweise unvollst&auml;ndig. Das '
                                                  'ist behoben.</li><li> RP-5388: Statistik-Editor: Beim Anzeigen von '
                                                  'Bemerkungen im Statistik-Editor konnte es zum Fehler '
                                                  '&quot;<I>FmeaStatAttachment&gt;&gt;#notes not '
                                                  'understood</I>&quot;&nbsp; kommen. Das ist behoben.</li><li> '
                                                  'RP-5392: FMEA-Formblatt: Nach dem Einblenden einer Ma&szlig;nahme '
                                                  'bei einer mehrfach verlinkten Ursache war im FMEA-Formblatt keine '
                                                  'individuelle Bewertung f&uuml;r den Ma&szlig;nahmenstand mit der '
                                                  'Einblendung mehr m&ouml;glich. Das ist behoben.</li><li> RP-5397: '
                                                  'Prozessablauf-Diagramm: Die Darstellung der '
                                                  '&quot;<I>Benutzerdefinierten Attribute</I>&quot; in der '
                                                  'Referenzspalte war fehlerhaft. Das ist behoben.</li></UL>'))
        db.session.add(ServicePackDetail(service_pack_id=sp.id, language='en',
                                         contents='<p><B><U>General:</U></B></p><UL><li> RP-5381: Variants Matrix '
                                                  'Editor: Some object names in the rows and columns were not '
                                                  'displaying completely. This is now fixed.</li><li> RP-5388: '
                                                  'Statistics Editor: When displaying notes in the Statistics Editor, '
                                                  'the following error sometimes occurred: '
                                                  '&quot;<I>FmeaStatAttachment&gt;&gt;#notes not '
                                                  'understood</I>&quot;. This is now fixed.&nbsp;</li><li> RP-5392: '
                                                  'FMEA Form: For linked actions at a cause with multiple references, '
                                                  'it was not possible to assign a new valuation, which only applied '
                                                  'to the linked location. This has been fixed.</li><li> RP-5397: '
                                                  'Process Flow Diagram<I>: User-defined attributes </I>&nbsp;were '
                                                  'displaying incorrectly in the Reference column. This is now '
                                                  'fixed.</li></UL><HR/><p><B><U>Allgemein:</U></B></p><UL><li> '
                                                  'RP-5381: Varianten-Matrix-Editor: Die Darstellung der '
                                                  'Objekt-Bezeichnungen in den Zeilen bzw. Spalten waren teilweise '
                                                  'unvollst&auml;ndig. Das ist behoben.</li><li> RP-5388: '
                                                  'Statistik-Editor: Beim Anzeigen von Bemerkungen im '
                                                  'Statistik-Editor konnte es zum Fehler '
                                                  '&quot;<I>FmeaStatAttachment&gt;&gt;#notes not '
                                                  'understood</I>&quot;&nbsp; kommen. Das ist behoben.</li><li> '
                                                  'RP-5392: FMEA-Formblatt: Nach dem Einblenden einer Ma&szlig;nahme '
                                                  'bei einer mehrfach verlinkten Ursache war im FMEA-Formblatt keine '
                                                  'individuelle Bewertung f&uuml;r den Ma&szlig;nahmenstand mit der '
                                                  'Einblendung mehr m&ouml;glich. Das ist behoben.</li><li> RP-5397: '
                                                  'Prozessablauf-Diagramm: Die Darstellung der '
                                                  '&quot;<I>Benutzerdefinierten Attribute</I>&quot; in der '
                                                  'Referenzspalte war fehlerhaft. Das ist behoben.</li></UL>'))
        description = 'Version 6.5 0170'
        version_number = int(description.split(' ')[-1])
        db.session.add(
            ServicePack(description=description, version_number=version_number,
                        release_date=datetime(2018, 12, 31, 23, 59, 59, 00)))
        sp = ServicePack.query.filter_by(version_number=version_number).first()
        db.session.add(ServicePackDetail(service_pack_id=sp.id, language='de',
                                         contents='<p><B><U>General:</U></B></p><UL><li> RP-4755: The attributes '
                                                  '&quot;<I>Lower Limit</I>&quot; and &quot;<I>Upper Limit</I>&quot; '
                                                  'now can be assigned as variant specific values.</li><li> RP-4801: '
                                                  'The suggestion list in the new Input Collector can now be faded in '
                                                  'and out.</li><li> RP-5162: CSS Action Tracking: After a module is '
                                                  'updated, the actions modified on the CARM NG Server are now '
                                                  'correctly transferred from this module to the fme.<P>Note: the '
                                                  'latest version of the CARM NG Server is required.</li><li> '
                                                  'RP-5214: Terminology and translation: Using the menu commands '
                                                  '&quot;Set reference name as translation&quot; and &quot;Set '
                                                  'translation as reference language name&quot; translations can be '
                                                  'transferred from the reference language to a translation language '
                                                  'and vice versa. This is also possible with PIM Bookmarks.</li><li> '
                                                  'RP-5218: Personal Information Manager: The PIM Editor can now be '
                                                  'added to Presentation Print and Web Publisher under '
                                                  '&quot;File-related documents&quot;. The entire public PIM Bookmark '
                                                  'collection is output. Private PIM entries are not intended to be '
                                                  'output here.</li><li> RP-5391: Search and Filter: searching for '
                                                  'the file name of documents embedded in notes now also takes into '
                                                  'account the original file name of the embedded file. You can also '
                                                  'search for &quot;<I>embeddedDocument</I>&quot; to find only the '
                                                  'notes with embedded documents.</li><li> RP-5418: Sorting &quot;by '
                                                  'number&quot; did not work reliably when using special characters '
                                                  'like \'_\' or \'?\' as (user-defined) numbers. This has been '
                                                  'fixed.</li><li> RP-5420: In lists with a tree view, a level can '
                                                  'now be folded/unfolded using the mouse:<UL><LI>Ctrl + left-click: '
                                                  'fold/unfold level<LI>Ctrl + Shift + left-click: fold/unfold the '
                                                  'current element and its neighbours</UL></li><li> RP-5428: When '
                                                  'printing, there are now additional placeholders for the '
                                                  'header/footer to print the document number (%N) and the version '
                                                  'index (%I).</li><li> RP-5433: When comparing files in the '
                                                  'Consolidation Desktop an internal failure '
                                                  '&quot;&quot;UndefinedObject&gt;&gt;#valueFor:object: not '
                                                  'understood&quot; sometimes occurred. This has been fixed.</li><li> '
                                                  'RP-5435: The menu option: &quot;Help | Update program '
                                                  'version&quot; is only executed if the IQ-Software is installed in '
                                                  'a valid/correct state on the computer. If this is not the case, '
                                                  'the command terminates with an error message.</li><li> RP-5477: A '
                                                  'new option &quot;Merge system elements with the same name &quot; '
                                                  'has been added to the import dialog &quot;Import '
                                                  'characteristics&quot;. If this option is active, system elements '
                                                  'with the same name are merged during the import.</li><li> RP-5488: '
                                                  'Control Plan Layout &quot;PLP-IATF 16989&quot;:<P>If the document '
                                                  'setting &quot;Control Plan | Use reaction plan/control method as '
                                                  'actions &quot; is active, the action attributes &quot;To be '
                                                  'included in Control Plan &quot; as well as &quot;...as control '
                                                  'method &quot; and &quot;...as reaction plan &quot; are also taken '
                                                  'into account and the actions are listed in the corresponding '
                                                  'columns (previously these attributes were not evaluated).</li><li> '
                                                  'RP-5528: Statistics/Action Tracking: planned deadlines can now be '
                                                  'evaluated starting from the creation date of the analysis. '
                                                  '<P></li></UL><p><B><U>CARM Server:</U></B></p><UL><li> RP-5324: If '
                                                  'an action has been uploaded to the CARM-NG Server (<I>CSS Action '
                                                  'Tracking</I>), its state will be indicated by an object '
                                                  'icon.</li><li> RP-5529: Module transitions of failures now '
                                                  'incorporate their anchor when adding a '
                                                  'module.</li></UL><p><B><U>Deadline Editor:</U></B></p><UL><li> '
                                                  'RP-5408: Deadline Editor (IQ structure - failure view): When the '
                                                  'document setting &quot;Use safety failure path for RPN '
                                                  'calculation&quot; is active, then the value of the secured path is '
                                                  'used for the calculation for the B column.</li><li> RP-5409: '
                                                  'Deadline Editor (IQ structure - failure view):&nbsp; When the '
                                                  'document setting &quot;Use safety failure path for RPN '
                                                  'calculation&quot; is active, then the value of the secured path is '
                                                  'used for the calculation for the RPN column.</li><li> RP-5414: '
                                                  'Deadline Editor (IQ structure - failure view):&nbsp; When the '
                                                  'document setting &quot;Use safety failure path for RPN '
                                                  'calculation&quot; is active, then the value of the secured path is '
                                                  'used for the calculation for the&nbsp; SxO '
                                                  'column.</li></UL><p><B><U>Only with maintenance '
                                                  'license:</U></B></p><UL><li> RP-4914: Summary Functions and notes '
                                                  'template: There are two new placeholders available: <P>1. MAXRPN: '
                                                  'determines the maximum RPN from the last completed revision state '
                                                  '(highest risk) <P>2. MAXDATE: determines the deadline furthest in '
                                                  'the future from the last rated revision state (i.e. when the '
                                                  'project is expected to be completed).&nbsp;</li><li> RP-5254: '
                                                  'Placeholder &amp; Summary Functions in Notes: If a variant is '
                                                  'specified as a base parameter ((%base) e.g. name of project, '
                                                  'structure, variant etc.), then this will be active for the '
                                                  'placeholder evaluation. If no variant is specified, '
                                                  'an active variant will remain active. If no variant is active and '
                                                  'none are specified as base parameters, the evaluation is based on '
                                                  'the parent structure or the FMEA form etc.. If the base parameter '
                                                  'is not clear (e.g. several variants for a single FMEA form/ '
                                                  'structure), then it is not defined which variant is used in the '
                                                  'evaluation. <BR><U>Recommendation</U>: if variants are used as a '
                                                  'base parameter, these should be unique to each note, '
                                                  'otherwise confusion may '
                                                  'occur.</li></UL><HR/><p><B><U>Allgemein:</U></B></p><UL><li> '
                                                  'RP-4755: Die Attribute &quot;<I>Oberer Grenzwert</I>&quot; und '
                                                  '&quot;<I>Unterer Grenzwert</I>&quot; k&ouml;nnen nun auch '
                                                  'variantenspezifisch vergeben werden.</li><li> RP-4801: Die '
                                                  'Vorschlagsliste in der neuen Sammeleingabe kann nun nach Bedarf '
                                                  'aus- und eingeblendet werden.</li><li> RP-5162: CSS Action '
                                                  'Tracking: nach einer Modulaktualisierung werden die am '
                                                  'CARM-NG-Server modifizierten Ma&szlig;nahmen aus diesem Modul nun '
                                                  'korrekt in die fme &uuml;bernommen.<P>Hinweis: dazu ist die '
                                                  'aktuelle Version des CARM-NG-Servers n&ouml;tig.</li><li> RP-5214: '
                                                  'Im Verwaltungseditor f&uuml;r Terminologie k&ouml;nnen mit den '
                                                  'Men&uuml;befehlen<I>&nbsp;&quot;Referenzsprache als '
                                                  '&Uuml;bersetzung &uuml;bernehmen&quot;</I> '
                                                  'bzw.<I>&nbsp;&quot;&Uuml;bersetzung als Referenzsprache '
                                                  '&uuml;bernehmen&quot;</I>&nbsp;&Uuml;bersetzungen von der '
                                                  'Referenzsprache in eine &Uuml;bersetzungssprache und umgekehrt '
                                                  '&uuml;bertragen werden. Dies ist auch f&uuml;r PIM-Lesezeichen '
                                                  'm&ouml;glich.</li><li> RP-5218: Personal Information Manager: der '
                                                  'PIM-Editor kann nun unter<I>&nbsp;&quot;Dateibezogenen '
                                                  'Dokumenten&quot; </I>im Pr&auml;sentationsdruck und WebPublisher '
                                                  'hinzugef&uuml;gt werden. Ausgegeben wird immer die gesamte '
                                                  '&ouml;ffentliche PIM-Lesezeichen-Sammlung. Private '
                                                  'PIM-Eintr&auml;ge sind hier nicht f&uuml;r eine Ausgabe '
                                                  'vorgesehen.</li><li> RP-5391: Suchen und Filtern: die Suche nach '
                                                  'dem Dateinamen von in Bemerkungen eingebetteten Dokumenten '
                                                  'ber&uuml;cksichtigt nun auch den urspr&uuml;nglichen Dateinamen '
                                                  'der eingebetteten Datei. Weiterhin kann auch nach<I> '
                                                  '&quot;embeddedDocument&quot;</I>&nbsp;gesucht werden um nur die '
                                                  'Bemerkungen mit eingebetteten Dokumenten zu finden.</li><li> '
                                                  'RP-5418: Die Sortierung &quot;nach Nummer&quot; hat bei Verwendung '
                                                  'von Sonderzeichen wie \'_\' oder \'?\' als (benutzerdefinierte) '
                                                  'Nummer nicht zuverl&auml;ssig funktioniert. Dies ist '
                                                  'behoben.</li><li> RP-5420: In Listen mit Baumdarstellung kann eine '
                                                  'Ebene jetzt durch Mausklick ein-/aufgefaltet werden:<UL><LI>Ctrl + '
                                                  '&lt;Linke Maustaste&gt; : Ebene ein-/auffalten<LI>Ctrl + Shift + '
                                                  '&lt;Linke Maustaste&gt; : aktuelles Element und seine Nachbarn '
                                                  'ein-/auffalten</UL></li><li> RP-5428: Beim Drucken gibt es '
                                                  'f&uuml;r die Kopf-/Fu&szlig;zeile zus&auml;tzliche Platzhalter, '
                                                  'um die Dokumentnummer (%N) und den Versionsindex (%I) zu '
                                                  'drucken.</li><li> RP-5433: Beim Dateivergleich im '
                                                  'Konsolidierungsdesktop konnte es zum internen Fehler: '
                                                  '&quot;UndefinedObject&gt;&gt;#valueFor:object: not '
                                                  'understood&quot; kommen. Dies ist behoben.</li><li> RP-5435: Die '
                                                  'Funktion<I>&nbsp;&quot;Programmversion '
                                                  'aktualisieren&quot;</I>&nbsp;wird nur dann ausgef&uuml;hrt, '
                                                  'wenn die IQ-Software in einem validen Zustand auf dem Rechner '
                                                  'installiert ist. Ist das nicht der Fall, dann bricht die Funktion '
                                                  'mit einer Fehlermeldung ab.</li><li> RP-5477: Im Import-Dialog '
                                                  '<I>&quot;Merkmale importieren&quot;</I>&nbsp;wurde eine neue '
                                                  'Optio<I>n &quot;Systemelemente mit gleichem Namen '
                                                  'zusammenfassen&quot; </I>hinzugef&uuml;gt. Wenn die Option aktiv '
                                                  'ist, dann werden beim Import Systemelemente mit gleichem Namen '
                                                  'zusammengefasst.</li><li> RP-5488: Contol-Plan Layout '
                                                  '&quot;PLP-IATF 16989&quot;:<P>Wenn die '
                                                  'Dokumenteinstellung<I>&nbsp;&quot;Control-Plan | '
                                                  'Lenkungsmethode/Reaktionsplan als Ma&szlig;nahmen '
                                                  'f&uuml;hren&quot; </I>aktiv ist, dann werden auch im '
                                                  'Layout<I>&nbsp;&quot;PLP-IATF 16989&quot;</I>&nbsp;des '
                                                  'Control-Plans die Ma&szlig;nahmenattribute<I>&nbsp;&quot;Soll im '
                                                  'Control-Plan enthalten sein&quot;</I>&nbsp;und <I>&quot;...als '
                                                  'Lenkungsmethode&quot;</I> bzw.<I>&nbsp;&quot;...als '
                                                  'Reaktionsplan&quot;</I>&nbsp;ber&uuml;cksichtigt und die '
                                                  'Ma&szlig;nahmen in den entsprechenden Spalten aufgelistet (bisher '
                                                  'wurden diese Attribute nicht ausgewertet).</li><li> RP-5528: '
                                                  'Statistik-Ma&szlig;nahmenverfolgung: <P>Optional k&ouml;nnen ab '
                                                  'dem Erstellungsdatum der Analyse die geplanten Termine (Deadlines) '
                                                  'ausgewertet '
                                                  'werden.</li></UL><p><B><U>CARM-Server:</U></B></p><UL><li> '
                                                  'RP-5324: Wurde eine Ma&szlig;nahme zum CARM-NG-Server (<I>CSS '
                                                  'Action Tracking</I>) &uuml;bertragen, wird dieser Zustand durch '
                                                  'ein entsprechendes Objekt-Icon visualisiert. <P><BR></li><li> '
                                                  'RP-5529: Modul&uuml;berg&auml;nge von Fehlfunktionen '
                                                  'ber&uuml;cksichtigen beim Modul einf&uuml;gen nun ihren '
                                                  'Anker.</li></UL><p><B><U>Terminverfolgung:</U></B></p><UL><li> '
                                                  'RP-5408: Terminverfolgung IQ-Fehlersicht: Wenn die '
                                                  'Dokumenteinstellung<I>&nbsp;&quot;Bei der RPZ-Berechnung '
                                                  'abgesicherten Pfad verwenden&quot;</I>&nbsp;eingeschaltet ist, '
                                                  'dann wird der Wert des abgesicherten Pfades zur Berechnung '
                                                  'f&uuml;r die B-Spalte verwendet.</li><li> RP-5409: '
                                                  'Terminverfolgung IQ-Fehlersicht: Wenn die Dokumenteinstellung<I> '
                                                  '&quot;Bei der RPZ-Berechnung abgesicherten Pfad '
                                                  'verwenden&quot;</I> eingeschaltet ist, dann wird der Wert des '
                                                  'abgesicherten Pfades zur Berechnung f&uuml;r die RPZ-Spalte '
                                                  'verwendet.</li><li> RP-5414: Terminverfolgung IQ-Fehlersicht: Wenn '
                                                  'die Dokumenteinstellung<I>&nbsp;&quot;Bei der RPZ-Berechnung '
                                                  'abgesicherten Pfad verwenden&quot;</I>&nbsp;eingeschaltet ist, '
                                                  'dann wird der Wert des abgesicherten Pfades zur Berechnung '
                                                  'f&uuml;r die BxA-Spalte '
                                                  'verwendet.</li></UL><p><B><U>Wartungskundenfunktionalit&auml;t:</U'
                                                  '></B></p><UL><li> RP-4914: Es sind nun zwei neue Platzhalter bei '
                                                  'den&nbsp; Summary-Functions und Bemerkungsvorlagen&nbsp; '
                                                  'verf&uuml;gbar:<P>1. MAXRPN: ermittelt die maximale RPZ aus den '
                                                  'letzten abgeschlossenen Ma&szlig;nahmenst&auml;nden ('
                                                  'gr&ouml;&szlig;tes Risiko) <P>2. MAXDATE: ermittelt den am '
                                                  'weitesten in der Zukunft liegenden Termin aus den offenen '
                                                  'Ma&szlig;nahmen in den letzten bewerteten '
                                                  'Ma&szlig;nahmenst&auml;nden (wann ist das Projekt voraussichtlich '
                                                  'abgeschlossen).</li><li> RP-5254: Platzhalter und '
                                                  'Summary-Functions in Bemerkungen: wenn als Datenbasis (%base) eine '
                                                  'Variante angegeben wird, dann wird diese nun f&uuml;r die '
                                                  'Evaluierung der Platzhalter aktiviert. Wenn keine Variante '
                                                  'angegeben ist, dann bleibt eine ggf. aktive Variante aktiv. Ist '
                                                  'keine Variante aktiv und keine als Datenbasis angegeben, '
                                                  'dann erfolgt die Evaluierung auf Basis der Mutterstruktur bzw. des '
                                                  'Formblattes etc. Wenn die Datenbasis nicht eindeutig ist (z.B. '
                                                  'mehrere Varianten f&uuml;r ein Formblatt/Struktur), dann ist nicht '
                                                  'definiert, welche Variante f&uuml;r die Evaluierung herangezogen '
                                                  'wird. <BR><U>Empfehlung</U><B>: </B>wenn Varianten als Datenbasis '
                                                  'benutzt werden, dann sollten diese je Bemerkung eindeutig sein, '
                                                  'da es ansonsten zu Verwirrung kommen kann.</li></UL>'))
        db.session.add(ServicePackDetail(service_pack_id=sp.id, language='en',
                                         contents='<p><B><U>General:</U></B></p><UL><li> RP-4755: The attributes '
                                                  '&quot;<I>Lower Limit</I>&quot; and &quot;<I>Upper Limit</I>&quot; '
                                                  'now can be assigned as variant specific values.</li><li> RP-4801: '
                                                  'The suggestion list in the new Input Collector can now be faded in '
                                                  'and out.</li><li> RP-5162: CSS Action Tracking: After a module is '
                                                  'updated, the actions modified on the CARM NG Server are now '
                                                  'correctly transferred from this module to the fme.<P>Note: the '
                                                  'latest version of the CARM NG Server is required.</li><li> '
                                                  'RP-5214: Terminology and translation: Using the menu commands '
                                                  '&quot;Set reference name as translation&quot; and &quot;Set '
                                                  'translation as reference language name&quot; translations can be '
                                                  'transferred from the reference language to a translation language '
                                                  'and vice versa. This is also possible with PIM Bookmarks.</li><li> '
                                                  'RP-5218: Personal Information Manager: The PIM Editor can now be '
                                                  'added to Presentation Print and Web Publisher under '
                                                  '&quot;File-related documents&quot;. The entire public PIM Bookmark '
                                                  'collection is output. Private PIM entries are not intended to be '
                                                  'output here.</li><li> RP-5391: Search and Filter: searching for '
                                                  'the file name of documents embedded in notes now also takes into '
                                                  'account the original file name of the embedded file. You can also '
                                                  'search for &quot;<I>embeddedDocument</I>&quot; to find only the '
                                                  'notes with embedded documents.</li><li> RP-5418: Sorting &quot;by '
                                                  'number&quot; did not work reliably when using special characters '
                                                  'like \'_\' or \'?\' as (user-defined) numbers. This has been '
                                                  'fixed.</li><li> RP-5420: In lists with a tree view, a level can '
                                                  'now be folded/unfolded using the mouse:<UL><LI>Ctrl + left-click: '
                                                  'fold/unfold level<LI>Ctrl + Shift + left-click: fold/unfold the '
                                                  'current element and its neighbours</UL></li><li> RP-5428: When '
                                                  'printing, there are now additional placeholders for the '
                                                  'header/footer to print the document number (%N) and the version '
                                                  'index (%I).</li><li> RP-5433: When comparing files in the '
                                                  'Consolidation Desktop an internal failure '
                                                  '&quot;&quot;UndefinedObject&gt;&gt;#valueFor:object: not '
                                                  'understood&quot; sometimes occurred. This has been fixed.</li><li> '
                                                  'RP-5435: The menu option: &quot;Help | Update program '
                                                  'version&quot; is only executed if the IQ-Software is installed in '
                                                  'a valid/correct state on the computer. If this is not the case, '
                                                  'the command terminates with an error message.</li><li> RP-5477: A '
                                                  'new option &quot;Merge system elements with the same name &quot; '
                                                  'has been added to the import dialog &quot;Import '
                                                  'characteristics&quot;. If this option is active, system elements '
                                                  'with the same name are merged during the import.</li><li> RP-5488: '
                                                  'Control Plan Layout &quot;PLP-IATF 16989&quot;:<P>If the document '
                                                  'setting &quot;Control Plan | Use reaction plan/control method as '
                                                  'actions &quot; is active, the action attributes &quot;To be '
                                                  'included in Control Plan &quot; as well as &quot;...as control '
                                                  'method &quot; and &quot;...as reaction plan &quot; are also taken '
                                                  'into account and the actions are listed in the corresponding '
                                                  'columns (previously these attributes were not evaluated).</li><li> '
                                                  'RP-5528: Statistics/Action Tracking: planned deadlines can now be '
                                                  'evaluated starting from the creation date of the analysis. '
                                                  '<P></li></UL><p><B><U>CARM Server:</U></B></p><UL><li> RP-5324: If '
                                                  'an action has been uploaded to the CARM-NG Server (<I>CSS Action '
                                                  'Tracking</I>), its state will be indicated by an object '
                                                  'icon.</li><li> RP-5529: Module transitions of failures now '
                                                  'incorporate their anchor when adding a '
                                                  'module.</li></UL><p><B><U>Deadline Editor:</U></B></p><UL><li> '
                                                  'RP-5408: Deadline Editor (IQ structure - failure view): When the '
                                                  'document setting &quot;Use safety failure path for RPN '
                                                  'calculation&quot; is active, then the value of the secured path is '
                                                  'used for the calculation for the B column.</li><li> RP-5409: '
                                                  'Deadline Editor (IQ structure - failure view):&nbsp; When the '
                                                  'document setting &quot;Use safety failure path for RPN '
                                                  'calculation&quot; is active, then the value of the secured path is '
                                                  'used for the calculation for the RPN column.</li><li> RP-5414: '
                                                  'Deadline Editor (IQ structure - failure view):&nbsp; When the '
                                                  'document setting &quot;Use safety failure path for RPN '
                                                  'calculation&quot; is active, then the value of the secured path is '
                                                  'used for the calculation for the&nbsp; SxO '
                                                  'column.</li></UL><p><B><U>Only with maintenance '
                                                  'license:</U></B></p><UL><li> RP-4914: Summary Functions and notes '
                                                  'template: There are two new placeholders available: <P>1. MAXRPN: '
                                                  'determines the maximum RPN from the last completed revision state '
                                                  '(highest risk) <P>2. MAXDATE: determines the deadline furthest in '
                                                  'the future from the last rated revision state (i.e. when the '
                                                  'project is expected to be completed).&nbsp;</li><li> RP-5254: '
                                                  'Placeholder &amp; Summary Functions in Notes: If a variant is '
                                                  'specified as a base parameter ((%base) e.g. name of project, '
                                                  'structure, variant etc.), then this will be active for the '
                                                  'placeholder evaluation. If no variant is specified, '
                                                  'an active variant will remain active. If no variant is active and '
                                                  'none are specified as base parameters, the evaluation is based on '
                                                  'the parent structure or the FMEA form etc.. If the base parameter '
                                                  'is not clear (e.g. several variants for a single FMEA form/ '
                                                  'structure), then it is not defined which variant is used in the '
                                                  'evaluation. <BR><U>Recommendation</U>: if variants are used as a '
                                                  'base parameter, these should be unique to each note, '
                                                  'otherwise confusion may '
                                                  'occur.</li></UL><HR/><p><B><U>Allgemein:</U></B></p><UL><li> '
                                                  'RP-4755: Die Attribute &quot;<I>Oberer Grenzwert</I>&quot; und '
                                                  '&quot;<I>Unterer Grenzwert</I>&quot; k&ouml;nnen nun auch '
                                                  'variantenspezifisch vergeben werden.</li><li> RP-4801: Die '
                                                  'Vorschlagsliste in der neuen Sammeleingabe kann nun nach Bedarf '
                                                  'aus- und eingeblendet werden.</li><li> RP-5162: CSS Action '
                                                  'Tracking: nach einer Modulaktualisierung werden die am '
                                                  'CARM-NG-Server modifizierten Ma&szlig;nahmen aus diesem Modul nun '
                                                  'korrekt in die fme &uuml;bernommen.<P>Hinweis: dazu ist die '
                                                  'aktuelle Version des CARM-NG-Servers n&ouml;tig.</li><li> RP-5214: '
                                                  'Im Verwaltungseditor f&uuml;r Terminologie k&ouml;nnen mit den '
                                                  'Men&uuml;befehlen<I>&nbsp;&quot;Referenzsprache als '
                                                  '&Uuml;bersetzung &uuml;bernehmen&quot;</I> '
                                                  'bzw.<I>&nbsp;&quot;&Uuml;bersetzung als Referenzsprache '
                                                  '&uuml;bernehmen&quot;</I>&nbsp;&Uuml;bersetzungen von der '
                                                  'Referenzsprache in eine &Uuml;bersetzungssprache und umgekehrt '
                                                  '&uuml;bertragen werden. Dies ist auch f&uuml;r PIM-Lesezeichen '
                                                  'm&ouml;glich.</li><li> RP-5218: Personal Information Manager: der '
                                                  'PIM-Editor kann nun unter<I>&nbsp;&quot;Dateibezogenen '
                                                  'Dokumenten&quot; </I>im Pr&auml;sentationsdruck und WebPublisher '
                                                  'hinzugef&uuml;gt werden. Ausgegeben wird immer die gesamte '
                                                  '&ouml;ffentliche PIM-Lesezeichen-Sammlung. Private '
                                                  'PIM-Eintr&auml;ge sind hier nicht f&uuml;r eine Ausgabe '
                                                  'vorgesehen.</li><li> RP-5391: Suchen und Filtern: die Suche nach '
                                                  'dem Dateinamen von in Bemerkungen eingebetteten Dokumenten '
                                                  'ber&uuml;cksichtigt nun auch den urspr&uuml;nglichen Dateinamen '
                                                  'der eingebetteten Datei. Weiterhin kann auch nach<I> '
                                                  '&quot;embeddedDocument&quot;</I>&nbsp;gesucht werden um nur die '
                                                  'Bemerkungen mit eingebetteten Dokumenten zu finden.</li><li> '
                                                  'RP-5418: Die Sortierung &quot;nach Nummer&quot; hat bei Verwendung '
                                                  'von Sonderzeichen wie \'_\' oder \'?\' als (benutzerdefinierte) '
                                                  'Nummer nicht zuverl&auml;ssig funktioniert. Dies ist '
                                                  'behoben.</li><li> RP-5420: In Listen mit Baumdarstellung kann eine '
                                                  'Ebene jetzt durch Mausklick ein-/aufgefaltet werden:<UL><LI>Ctrl + '
                                                  '&lt;Linke Maustaste&gt; : Ebene ein-/auffalten<LI>Ctrl + Shift + '
                                                  '&lt;Linke Maustaste&gt; : aktuelles Element und seine Nachbarn '
                                                  'ein-/auffalten</UL></li><li> RP-5428: Beim Drucken gibt es '
                                                  'f&uuml;r die Kopf-/Fu&szlig;zeile zus&auml;tzliche Platzhalter, '
                                                  'um die Dokumentnummer (%N) und den Versionsindex (%I) zu '
                                                  'drucken.</li><li> RP-5433: Beim Dateivergleich im '
                                                  'Konsolidierungsdesktop konnte es zum internen Fehler: '
                                                  '&quot;UndefinedObject&gt;&gt;#valueFor:object: not '
                                                  'understood&quot; kommen. Dies ist behoben.</li><li> RP-5435: Die '
                                                  'Funktion<I>&nbsp;&quot;Programmversion '
                                                  'aktualisieren&quot;</I>&nbsp;wird nur dann ausgef&uuml;hrt, '
                                                  'wenn die IQ-Software in einem validen Zustand auf dem Rechner '
                                                  'installiert ist. Ist das nicht der Fall, dann bricht die Funktion '
                                                  'mit einer Fehlermeldung ab.</li><li> RP-5477: Im Import-Dialog '
                                                  '<I>&quot;Merkmale importieren&quot;</I>&nbsp;wurde eine neue '
                                                  'Optio<I>n &quot;Systemelemente mit gleichem Namen '
                                                  'zusammenfassen&quot; </I>hinzugef&uuml;gt. Wenn die Option aktiv '
                                                  'ist, dann werden beim Import Systemelemente mit gleichem Namen '
                                                  'zusammengefasst.</li><li> RP-5488: Contol-Plan Layout '
                                                  '&quot;PLP-IATF 16989&quot;:<P>Wenn die '
                                                  'Dokumenteinstellung<I>&nbsp;&quot;Control-Plan | '
                                                  'Lenkungsmethode/Reaktionsplan als Ma&szlig;nahmen '
                                                  'f&uuml;hren&quot; </I>aktiv ist, dann werden auch im '
                                                  'Layout<I>&nbsp;&quot;PLP-IATF 16989&quot;</I>&nbsp;des '
                                                  'Control-Plans die Ma&szlig;nahmenattribute<I>&nbsp;&quot;Soll im '
                                                  'Control-Plan enthalten sein&quot;</I>&nbsp;und <I>&quot;...als '
                                                  'Lenkungsmethode&quot;</I> bzw.<I>&nbsp;&quot;...als '
                                                  'Reaktionsplan&quot;</I>&nbsp;ber&uuml;cksichtigt und die '
                                                  'Ma&szlig;nahmen in den entsprechenden Spalten aufgelistet (bisher '
                                                  'wurden diese Attribute nicht ausgewertet).</li><li> RP-5528: '
                                                  'Statistik-Ma&szlig;nahmenverfolgung: <P>Optional k&ouml;nnen ab '
                                                  'dem Erstellungsdatum der Analyse die geplanten Termine (Deadlines) '
                                                  'ausgewertet '
                                                  'werden.</li></UL><p><B><U>CARM-Server:</U></B></p><UL><li> '
                                                  'RP-5324: Wurde eine Ma&szlig;nahme zum CARM-NG-Server (<I>CSS '
                                                  'Action Tracking</I>) &uuml;bertragen, wird dieser Zustand durch '
                                                  'ein entsprechendes Objekt-Icon visualisiert. <P><BR></li><li> '
                                                  'RP-5529: Modul&uuml;berg&auml;nge von Fehlfunktionen '
                                                  'ber&uuml;cksichtigen beim Modul einf&uuml;gen nun ihren '
                                                  'Anker.</li></UL><p><B><U>Terminverfolgung:</U></B></p><UL><li> '
                                                  'RP-5408: Terminverfolgung IQ-Fehlersicht: Wenn die '
                                                  'Dokumenteinstellung<I>&nbsp;&quot;Bei der RPZ-Berechnung '
                                                  'abgesicherten Pfad verwenden&quot;</I>&nbsp;eingeschaltet ist, '
                                                  'dann wird der Wert des abgesicherten Pfades zur Berechnung '
                                                  'f&uuml;r die B-Spalte verwendet.</li><li> RP-5409: '
                                                  'Terminverfolgung IQ-Fehlersicht: Wenn die Dokumenteinstellung<I> '
                                                  '&quot;Bei der RPZ-Berechnung abgesicherten Pfad '
                                                  'verwenden&quot;</I> eingeschaltet ist, dann wird der Wert des '
                                                  'abgesicherten Pfades zur Berechnung f&uuml;r die RPZ-Spalte '
                                                  'verwendet.</li><li> RP-5414: Terminverfolgung IQ-Fehlersicht: Wenn '
                                                  'die Dokumenteinstellung<I>&nbsp;&quot;Bei der RPZ-Berechnung '
                                                  'abgesicherten Pfad verwenden&quot;</I>&nbsp;eingeschaltet ist, '
                                                  'dann wird der Wert des abgesicherten Pfades zur Berechnung '
                                                  'f&uuml;r die BxA-Spalte '
                                                  'verwendet.</li></UL><p><B><U>Wartungskundenfunktionalit&auml;t:</U'
                                                  '></B></p><UL><li> RP-4914: Es sind nun zwei neue Platzhalter bei '
                                                  'den&nbsp; Summary-Functions und Bemerkungsvorlagen&nbsp; '
                                                  'verf&uuml;gbar:<P>1. MAXRPN: ermittelt die maximale RPZ aus den '
                                                  'letzten abgeschlossenen Ma&szlig;nahmenst&auml;nden ('
                                                  'gr&ouml;&szlig;tes Risiko) <P>2. MAXDATE: ermittelt den am '
                                                  'weitesten in der Zukunft liegenden Termin aus den offenen '
                                                  'Ma&szlig;nahmen in den letzten bewerteten '
                                                  'Ma&szlig;nahmenst&auml;nden (wann ist das Projekt voraussichtlich '
                                                  'abgeschlossen).</li><li> RP-5254: Platzhalter und '
                                                  'Summary-Functions in Bemerkungen: wenn als Datenbasis (%base) eine '
                                                  'Variante angegeben wird, dann wird diese nun f&uuml;r die '
                                                  'Evaluierung der Platzhalter aktiviert. Wenn keine Variante '
                                                  'angegeben ist, dann bleibt eine ggf. aktive Variante aktiv. Ist '
                                                  'keine Variante aktiv und keine als Datenbasis angegeben, '
                                                  'dann erfolgt die Evaluierung auf Basis der Mutterstruktur bzw. des '
                                                  'Formblattes etc. Wenn die Datenbasis nicht eindeutig ist (z.B. '
                                                  'mehrere Varianten f&uuml;r ein Formblatt/Struktur), dann ist nicht '
                                                  'definiert, welche Variante f&uuml;r die Evaluierung herangezogen '
                                                  'wird. <BR><U>Empfehlung</U><B>: </B>wenn Varianten als Datenbasis '
                                                  'benutzt werden, dann sollten diese je Bemerkung eindeutig sein, '
                                                  'da es ansonsten zu Verwirrung kommen kann.</li></UL>'))
        db.session.commit()
    return


if __name__ == '__main__':
    build_sample_db()
