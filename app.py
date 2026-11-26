# Flake8 : noqa

import hashlib
import os
import subprocess
import sys
import threading
import time
import contextlib
import sqlite3
from pathlib import Path
from database.init_db import init
from database.db import query, execute
from auth.register import register, GOALS, RISKS
from auth.login import login, google_login
from auth.security import reset, verify, hash_password
from views import dashboard, portfolio, admin
from utils.alerts import check
from utils.stock_api import valid_symbol

try:
    init()
except Exception as exc:
    print('[DATABASE INITIALIZATION FAILED]', type(exc).__name__, exc, flush=True)
    raise SystemExit('Database initialization failed. Check database permissions and app/database files.') from exc

ROOT = Path(__file__).resolve().parent
ENV = ROOT / 'env'
REQUIREMENTS = ROOT / 'requirements.txt'
PACKAGES = ('streamlit', 'authlib', 'bcrypt', 'plotly', 'curl_cffi')


def verify_packages(python):
    failed = []
    for name in PACKAGES:
        result = subprocess.run([str(python), '-c', f'import {name}'],
            capture_output=True, text=True)
        print(f"[{('OK' if result.returncode == 0 else 'FAILED')}] {name}",
            flush=True)
        if result.returncode:
            failed.append(name)
            print(result.stderr, flush=True)
    return failed


def run_streamlit(python):
    environment = os.environ.copy()
    environment['STACKPULSE_LOCAL'] = '1'
    command = [str(python), '-m', 'streamlit', 'run', str(ROOT / 'app.py'),
        '--server.port=8501']
    process = subprocess.Popen(command, cwd=ROOT, env=environment)
    try:
        while process.poll() is None:
            if os.name == 'nt' and sys.stdin.isatty():
                import msvcrt
                if msvcrt.kbhit() and msvcrt.getwch() == '\x04':
                    break
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def launch():
    print('FIRST-RUN DEPENDENCY INSTALLER - LOCAL COMPUTER', flush=True)
    python = ENV / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        subprocess.check_call([sys.executable, '-m', 'venv', str(ENV)])
    pip = [str(python), '-m', 'pip']
    digest = hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()
    marker = ENV / '.requirements_hash'
    update = '--update' in sys.argv or 'update' in sys.argv
    if update or not marker.exists() or marker.read_text() != digest:
        subprocess.check_call(pip + ['install', '--upgrade', 'pip'])
        subprocess.check_call(pip + ['install', '--upgrade', '-r', str(
            REQUIREMENTS)])
    failed = verify_packages(python)
    if failed or subprocess.call(pip + ['check']):
        print('[REPAIR] Reinstalling project dependencies', flush=True)
        subprocess.check_call(pip + ['install', '--force-reinstall',
            '--no-cache-dir', '-r', str(REQUIREMENTS)])
        if verify_packages(python):
            raise SystemExit((
                    'Dependency repair failed; inspect th'
                    'e errors above.'
                ))
    subprocess.check_call(pip + ['check'])
    marker.write_text(digest)
    print('[READY] http://localhost:8501', flush=True)
    run_streamlit(python)


def running_in_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx(suppress_warning=True) is not None
    except Exception:
        return False


if __name__ == '__main__' and (not running_in_streamlit()):
    with contextlib.suppress(KeyboardInterrupt):
        launch()
    sys.exit(0)


def application():
    import streamlit as st

    @st.cache_resource(show_spinner=False)
    def browser_watch():
        if os.getenv('STACKPULSE_LOCAL') != '1':
            return
        from streamlit.runtime import Runtime
        runtime = Runtime.instance()

        def monitor():
            disconnected_at = None
            while True:
                if runtime.is_active_session(session_id):
                    disconnected_at = None
                elif disconnected_at is None:
                    disconnected_at = time.monotonic()
                elif time.monotonic() - disconnected_at >= 10:
                    if not runtime._session_mgr.list_active_sessions():
                        os._exit(0)
                time.sleep(1)
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        session_id = get_script_run_ctx().session_id
        threading.Thread(target=monitor, daemon=True).start()

    @st.cache_resource(show_spinner=False)
    def verify_active_environment():
        print(f'[ACTIVE ENV] {sys.prefix}', flush=True)
        return verify_packages(sys.executable)
    st.set_page_config(page_title='StackPulse India', page_icon='📈',
                       layout='wide')
    browser_watch()
    if (failed := verify_active_environment()):
        st.error('Dependency import failed: ' + ', '.join(failed))
        st.info((
                'Check requirements.txt and rebuild t'
                'he deployment environment.'))
        st.stop()

    def login_theme():
        st.markdown((
                '<style>\n    [data-testid="stAppViewC'
                'ontainer"], [data-testid="stHeader"]'
                ' {background:#10162b;color:#fff;}\n  '
                '  [data-testid="stHeader"] {display:'
                'none;}\n    .block-container {max-wid'
                'th: min(1600px, 96vw);padding:1.5rem'
                ' 2rem 1rem;min-height:100dvh;box-siz'
                'ing:border-box;}\n    .pulse-header {'
                'display:flex;align-items:center;just'
                'ify-content:space-between;color:#fff'
                ';padding:8px 0 16px;font-size:20px;f'
                'ont-weight:700;}\n    .pulse-header s'
                'mall {color:#a5b4fc;font-size:13px;f'
                'ont-weight:400;}\n    .pulse-header a'
                ' {color:#a5b4fc;text-decoration:none'
                ';}\n    .pulse-header a:hover {color:'
                '#6ee7b7;text-decoration:underline;}\n'
                '    .pulse-hero {background:#292052;'
                'border-radius:20px;padding:30px;colo'
                'r:#fff;min-height:clamp(440px, 65vh,'
                ' 720px);box-sizing:border-box;displa'
                'y:flex;flex-direction:column;justify'
                '-content:space-between;}\n    .pulse-'
                'hero h1 {color:#fff;font-size:clamp('
                '2rem,4vw,3rem);line-height:1.12;padd'
                'ing:12px 0;}\n    .pulse-hero p {colo'
                'r:#ddd9f8;margin:0 0 12px;}\n    .pul'
                'se-features {display:grid;grid-templ'
                'ate-columns:1fr 1fr;gap:10px;margin-'
                'top:12px;}\n    .pulse-features div {'
                'background:#ffffff12;border-radius:1'
                '0px;padding:clamp(12px,2vh,24px);col'
                'or:white;font-size:14px;}\n    .pulse'
                '-features b {display:block;font-size'
                ':20px;margin-bottom:4px;}\n    .st-ke'
                'y-account_panel {background:#1b243b;'
                'border-radius:20px;padding:26px;min-'
                'height:clamp(440px, 65vh, 720px);col'
                'or:#fff;}\n    .st-key-account_panel '
                'h2,.st-key-account_panel label,.st-k'
                'ey-account_panel label p,.st-key-acc'
                'ount_panel [data-testid="stMarkdownC'
                'ontainer"] p {color:#f1f5ff;}\n    .s'
                't-key-account_panel [data-testid="st'
                'CaptionContainer"] p {color:#b8bfd2;'
                '}\n    .st-key-account_panel [data-te'
                'stid="stForm"] {border:0;padding:0;}'
                '\n    .st-key-account_panel [data-bas'
                'eweb="input"],.st-key-account_panel '
                '[data-baseweb="select"] > div {backg'
                'round:#1b243b;border:1px solid #5964'
                '7e;border-radius:9px;}\n    .st-key-a'
                'ccount_panel input {color:#fff;backg'
                'round:transparent;caret-color:#fff;}'
                '\n    .st-key-account_panel input::pl'
                'aceholder {color:#aab4cc;}\n    .st-k'
                'ey-account_panel [data-baseweb="inpu'
                't"] button {background:transparent;c'
                'olor:#a5b4fc;}\n    .st-key-account_p'
                'anel [data-testid="stRadio"] [role="'
                'radiogroup"] {gap:6px;flex-wrap:wrap'
                ';}\n    .st-key-account_panel [data-t'
                'estid="stRadio"] label {padding:7px '
                '10px;border-radius:8px;margin:0;back'
                'ground:#26314b;}\n    .st-key-account'
                '_panel [data-testid="stRadio"] label'
                ':has(input:checked) {background:#704'
                '7df;}\n    .st-key-account_panel [dat'
                'a-testid="stRadio"] label > div:firs'
                't-child {display:none;}\n    .st-key-'
                'account_panel button[kind="primaryFo'
                'rmSubmit"] {background:linear-gradie'
                'nt(100deg,#7047df,#5265ed);border:0;'
                'color:white;min-height:44px;}\n    .s'
                't-key-account_panel button[kind="sec'
                'ondary"] {background:transparent;bor'
                'der:1px solid #59647e;color:#fff;}\n '
                '   .st-key-account_panel button:focu'
                's-visible,.st-key-account_panel labe'
                'l:focus-within {outline:2px solid #a'
                '5b4fc;outline-offset:2px;}\n    .puls'
                'e-footer {background:#1b243b;border-'
                'radius:12px;text-align:center;margin'
                '-top:1rem;padding:16px;color:#cbd5e1'
                ';font-size:13px;line-height:1.65;}\n '
                '   .pulse-footer a {color:#6ee7b7;te'
                'xt-decoration:none;}\n    @media(max-'
                'width:640px){.block-container{paddin'
                'g:1rem .8rem .25rem;}.pulse-hero,.st'
                '-key-account_panel{padding:18px;min-'
                'height:0;}.pulse-header{flex-wrap:wr'
                'ap;gap:8px;}.pulse-header small{disp'
                'lay:block;}}\n\n    .st-key-account_pa'
                'nel [data-baseweb="input"],\n    .st-'
                'key-account_panel [data-baseweb="bas'
                'e-input"],\n    .st-key-account_panel'
                ' [data-baseweb="input"] > div,\n    .'
                'st-key-account_panel [data-baseweb="'
                'select"] > div {background:#111827 !'
                'important;color:#f8fafc !important;}'
                '\n    .st-key-account_panel input {ba'
                'ckground:#111827 !important;color:#f'
                '8fafc !important;-webkit-text-fill-c'
                'olor:#f8fafc !important;caret-color:'
                '#fff;}\n    .st-key-account_panel inp'
                'ut::placeholder {color:#aebbd0 !impo'
                'rtant;-webkit-text-fill-color:#aebbd'
                '0 !important;opacity:1;}\n    .st-key'
                '-account_panel input:-webkit-autofil'
                'l {box-shadow:0 0 0 1000px #111827 i'
                'nset !important;-webkit-text-fill-co'
                'lor:#f8fafc !important;}\n    .st-key'
                '-account_panel [data-baseweb="input"'
                '] button {background:#111827 !import'
                'ant;color:#c7d2fe !important;}\n    .'
                'st-key-account_panel [data-testid="s'
                'tAlert"] [role="alert"],\n    .st-key'
                '-account_panel [data-testid="stAlert'
                'Container"] {background:#40212e !imp'
                'ortant;color:#fecaca !important;bord'
                'er-radius:8px;}\n    .st-key-account_'
                'panel [data-testid="stAlert"] p {col'
                'or:#fecaca !important;}\n    .st-key-'
                'account_panel [data-testid="stAlert"'
                ']:has([data-testid="stAlertContentSu'
                'ccess"]) p {color:#bbf7d0 !important'
                ';}\n    .st-key-account_panel [data-t'
                'estid="stCaptionContainer"],\n    .st'
                '-key-account_panel [data-testid="stC'
                'aptionContainer"] p,\n    .st-key-acc'
                'ount_panel [data-testid="stInputInst'
                'ructions"] {color:#c0cbe0 !important'
                ';}\n    .st-key-account_panel [data-t'
                'estid="stRadio"] label > div:first-c'
                'hild:not(:has(input)) {display:none '
                '!important;}\n    @media(min-width:64'
                '1px){.block-container [data-testid="'
                'stHorizontalBlock"]:has(.pulse-hero)'
                '{align-items:stretch;}.block-contain'
                'er [data-testid="stColumn"]:has(.st-'
                'key-account_panel){display:flex;flex'
                '-direction:column;}.st-key-account_p'
                'anel{flex:1;box-sizing:border-box;}}'
                '\n    </style><div class="pulse-heade'
                'r"><span>📈 StackPulse India</span><s'
                'mall><a href="https://stockanalytics'
                '.co.in/" target="_blank" rel="noopen'
                'er noreferrer">Stock Portfolio Analy'
                'tics ↗</a></small></div>'
            ), unsafe_allow_html=True)

    def account_banner():
        heights = [24, 39, 31, 53, 46, 67, 59, 88, 80, 98]
        bars = ''.join((f'''<rect x="{8 + i * 25}" y="{
            102 - h}" width="16" height="{h}" rx="3" fill="url
            (#{('purple' if i < 5 else 'green')})"/>''' for i, h in enumerate(
            heights)))
        st.markdown(
            (
                '<section class="pulse-hero">\n   '
                ' <div style="color:#b8a4ff;font-'
                'size:12px;font-weight:700">SMART'
                ' INVESTMENT TRACKING</div>\n    <'
                'h1>Track. Analyze. Grow.</h1><p>'
                'Your Indian stock portfolio. One'
                ' intelligent dashboard.</p>\n    '
                '<svg viewBox="0 0 260 105" width'
                '="100%" height="190" aria-hidden'
                '="true"><defs><linearGradient id'
                '="purple" x2="0" y2="1"><stop st'
                'op-color="#a78bfa"/><stop offset'
                '="1" stop-color="#5443c5"/></lin'
                'earGradient><linearGradient id="'
                'green" x2="0" y2="1"><stop stop-'
                'color="#6ee7b7"/><stop offset="1'
                '" stop-color="#0c8e85"/></linear'
                'Gradient></defs>'
                f'{bars}'
                '<path d="M10 73 L43 60 L68 66 L9'
                '4 43 L120 49 L145 27 L171 34 L19'
                '6 12 L220 20 L250 3" fill="none"'
                ' stroke="#fcd34d" stroke-width="'
                '2.5"/></svg>\n    <div class="pul'
                'se-features"><div><b style="colo'
                'r:#c4b5fd">◔</b>Portfolio</div><'
                'div><b style="color:#6ee7b7">↗</'
                'b>Profit / Loss</div><div><b sty'
                'le="color:#93c5fd">⟳</b>Recovery'
                '</div><div><b style="color:#fcd3'
                '4d">♧</b>Price Alerts</div></div'
                '></section>'
            ),
            unsafe_allow_html=True,
        )

    def footer():
        st.markdown((
                '<div class="pulse-footer"><strong st'
                'yle="color:#a5b4fc;font-size:16px">H'
                'ire a Python AI Developer</strong><d'
                'iv>Python Automation • AI / ML • Sto'
                'ck Analytics</div><div>Jinesh Paras '
                'Shah · <a href="mailto:jinesh9676@gm'
                'ail.com">Email</a> | <a href="tel:+9'
                '18799428255">Contact</a> | <a href="'
                'https://github.com/jinesh9676">GitHu'
                'b</a></div><small>StackPulse India ©'
                ' 2026 | Python · Streamlit · SQLite<'
                '/small></div>'
            ), unsafe_allow_html=True)
    if st.user.get('is_logged_in', False) and (not st.session_state.get('uid')
                                               ):
        try:
            if st.user.get('email_verified') is not True:
                raise ValueError('Google email must be verified')
            st.session_state.uid = google_login(st.user['sub'], st.user[
                'email'], st.user.get('name', 'Google user'))
        except (ValueError, sqlite3.IntegrityError) as e:
            st.error(str(e))
    uid = st.session_state.get('uid')
    rows = query((
            'SELECT * FROM users WHERE id=? AND s'
            "tatus='active'"
        ), (uid,)) if uid else []
    if not rows:
        st.session_state.pop('uid', None)
        login_theme()
        brand, account = st.columns([1, 1], gap='medium')
        with brand:
            account_banner()
        with account, st.container(key='account_panel'):
            panel_heading = st.empty()
            if st.user.get('is_logged_in', False) and st.button(
                    'Sign out of Google'):
                st.logout()
            mode = st.radio('Account', ['Login', 'Sign up', 'Reset password'],
                horizontal=True, label_visibility='collapsed')
            headings = {'Login': 'Welcome back 👋',
                'Sign up': 'Create your account',
                'Reset password': 'Reset your password'}
            panel_heading.markdown(f'## {headings[mode]}')
            if mode == 'Login':
                st.caption('Access your investment dashboard')
            try:
                if mode == 'Login':
                    with st.form('login'):
                        u = st.text_input('Username',
                            placeholder='Enter username')
                        p = st.text_input('Password', type='password',
                            placeholder='Enter password')
                        if st.form_submit_button('Sign in →', type='primary',
                            use_container_width=True):
                            uid = login(u, p)
                            if uid:
                                st.session_state.uid = uid
                                st.rerun()
                            else:
                                st.error(
                                    'Invalid credentials or inactive account')
                    try:
                        configured = 'auth' in st.secrets
                    except Exception:
                        configured = False
                    if configured and st.button('Continue with Google',
                        use_container_width=True):
                        st.login()
                    st.markdown((
                            '<div style="text-align:center;color:'
                            '#6ee7b7;font-size:12px">🛡 Password p'
                            'rotected account</div>'
                        ), unsafe_allow_html=True)
                elif mode == 'Sign up':
                    with st.form('signup'):
                        n = st.text_input('Full Name *')
                        u = st.text_input('Username *')
                        e = st.text_input('Email Address *')
                        m = st.text_input('Mobile Number')
                        p = st.text_input('Password *', type='password')
                        c = st.text_input('Confirm Password *',
                            type='password')
                        g = st.selectbox('Investment Goal', GOALS)
                        r = st.selectbox('Risk Profile', RISKS)
                        if st.form_submit_button('Register', type='primary',
                            use_container_width=True):
                            register(n, u, e, m, p, c, g, r)
                            st.success('Account created. Select Login.')
                else:
                    st.info((
                            'Request a reset token from the admin'
                            'istrator after identity verification'
                            '.'))
                    with st.form('reset'):
                        t = st.text_input('Reset token', type='password')
                        p = st.text_input('New password', type='password')
                        if st.form_submit_button('Reset', type='primary',
                            use_container_width=True):
                            reset(t, p)
                            st.success('Password updated')
            except ValueError as e:
                st.error(str(e))
            except sqlite3.IntegrityError:
                st.error('Username or email already exists.')
        footer()
        st.stop()
    st.title('📈 StackPulse India')
    user = rows[0]
    st.sidebar.write('Welcome, ' + user['full_name'])
    if st.sidebar.button('Logout'):
        st.session_state.clear()
        if st.user.get('is_logged_in', False):
            st.logout()
        st.rerun()
    menu = ['Dashboard', 'Portfolio', 'Profit / Loss', 'Recovery Tracker',
        'Alerts', 'Profile', 'Privacy']
    if user['role'] == 'admin':
        menu.append('Admin')
    page = st.sidebar.radio('Navigation', menu)
    try:
        notice = query("SELECT value FROM settings WHERE key='notice'")
        if notice and notice[0]['value']:
            st.info(notice[0]['value'])
        if page in ['Dashboard', 'Profit / Loss', 'Recovery Tracker']:
            dashboard.show(uid, page)
        elif page == 'Portfolio':
            portfolio.show(uid)
        elif page == 'Admin':
            admin.show(uid)
        elif page == 'Alerts':
            st.header('Price alerts')
            check(uid)
            with st.form('alert'):
                s = st.text_input('Symbol', 'TCS.NS').upper()
                p = st.number_input('Target ₹', min_value=0.01)
                t = st.selectbox('Type', ['Profit', 'Loss', 'Recovery'])
                if st.form_submit_button('Create alert'):
                    if valid_symbol(s):
                        execute((
                                'INSERT INTO alerts(user_id,stock_sym'
                                'bol,target_price,alert_type) VALUES('
                                '?,?,?,?)'), (uid, s, p, t))
                        st.rerun()
                    else:
                        st.error('Invalid symbol')
            a = query('SELECT * FROM alerts WHERE user_id=?', (uid,))
            st.dataframe(a)
            if a:
                aid = st.selectbox('Delete alert', [x['id'] for x in a])
                if st.button('Delete alert'):
                    execute('DELETE FROM alerts WHERE id=? AND user_id=?', (
                        aid, uid))
                    st.rerun()
            st.caption((
                    'Alerts evaluated when this page load'
                    's; no background notifications.'
                ))
        elif page == 'Profile':
            with st.form('profile'):
                n = st.text_input('Full name', user['full_name'])
                m = st.text_input('Mobile', user['mobile'] or '')
                g = st.selectbox('Goal', GOALS, index=GOALS.index(user[
                    'goal']) if user['goal'] in GOALS else 0)
                r = st.selectbox('Risk', RISKS, index=RISKS.index(user[
                    'risk']) if user['risk'] in RISKS else 0)
                if st.form_submit_button('Save profile'):
                    if not n.strip():
                        raise ValueError('Name required')
                    execute((
                            'UPDATE users SET full_name=?,mobile='
                            '?,goal=?,risk=? WHERE id=?'), (n, m, g, r, uid))
                    st.rerun()
            if user['password_hash']:
                with st.form('password'):
                    old = st.text_input('Current password', type='password')
                    new = st.text_input('New password', type='password')
                    if st.form_submit_button('Change password'):
                        if not verify(old, user['password_hash']):
                            st.error('Incorrect password')
                        else:
                            execute(
                                'UPDATE users SET password_hash=? WHERE id=?',
                                (hash_password(new), uid))
                            st.success('Updated')
        else:
            st.write((
                    'We store account details and portfol'
                    'io data. Administrators can view por'
                    'tfolios. We do not collect banking c'
                    'redentials, UPI PINs or broker passw'
                    'ords. Passwords are hashed with bcry'
                    'pt.'
                ))
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        execute((
                'INSERT INTO logs(user_id,error_type,'
                'description) VALUES(?,?,?)'), (uid, page, type(e).__name__))
        st.error('Operation failed. Contact administrator.')


application()
