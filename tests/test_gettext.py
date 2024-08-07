import flask

import flask_babel as babel
from flask_babel import gettext, lazy_gettext, lazy_ngettext, ngettext, get_babel


def test_basics():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale="de_DE")

    with app.test_request_context():
        assert gettext("Hello %(name)s!", name="Peter") == "Hallo Peter!"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 3) == "3 Äpfel"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "1 Apfel"


def test_template_basics():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale="de_DE")

    def t(x):
        return flask.render_template_string("{{ %s }}" % x)

    with app.test_request_context():
        assert t("gettext('Hello %(name)s!', name='Peter')") == "Hallo Peter!"
        assert t("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == "3 Äpfel"
        assert t("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == "1 Apfel"
        assert (
            flask.render_template_string(
                """
            {% trans %}Hello {{ name }}!{% endtrans %}
        """,
                name="Peter",
            ).strip()
            == "Hallo Peter!"
        )
        assert (
            flask.render_template_string(
                """
            {% trans num=3 %}{{ num }} Apple
            {%- pluralize %}{{ num }} Apples{% endtrans %}
        """,
                name="Peter",
            ).strip()
            == "3 Äpfel"
        )


def test_lazy_gettext():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale="de_DE")
    yes = lazy_gettext("Yes")
    with app.test_request_context():
        assert str(yes) == "Ja"
        assert yes.__html__() == "Ja"

    get_babel(app).default_locale = "en_US"
    with app.test_request_context():
        assert str(yes) == "Yes"
        assert yes.__html__() == "Yes"


def test_lazy_ngettext():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale="de_DE")
    one_apple = lazy_ngettext("%(num)s Apple", "%(num)s Apples", 1)
    with app.test_request_context():
        assert str(one_apple) == "1 Apfel"
        assert one_apple.__html__() == "1 Apfel"
    two_apples = lazy_ngettext("%(num)s Apple", "%(num)s Apples", 2)
    with app.test_request_context():
        assert str(two_apples) == "2 Äpfel"
        assert two_apples.__html__() == "2 Äpfel"


def test_lazy_gettext_defaultdomain():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale="de_DE", default_domain="test")
    first = lazy_gettext("first")

    with app.test_request_context():
        assert str(first) == "erste"

    get_babel(app).default_locale = "en_US"
    with app.test_request_context():
        assert str(first) == "first"


def test_list_translations():
    app = flask.Flask(__name__)
    b = babel.Babel(app, default_locale="de_DE")

    with app.app_context():
        translations = sorted(b.list_translations(), key=str)
        assert len(translations) == 3
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "de_DE"
        assert str(translations[2]) == "ja"


def test_list_translations_default_locale_exists():
    app = flask.Flask(__name__)
    b = babel.Babel(app, default_locale="de")

    with app.app_context():
        translations = sorted(b.list_translations(), key=str)
        assert len(translations) == 2
        assert str(translations[0]) == "de"
        assert str(translations[1]) == "ja"


def test_no_formatting():
    """
    Ensure we don't format strings unless a variable is passed.
    """
    app = flask.Flask(__name__)
    babel.Babel(app)

    with app.test_request_context():
        assert gettext("Test %s") == "Test %s"
        assert gettext("Test %(name)s", name="test") == "Test test"
        assert gettext("Test %s") % "test" == "Test test"


def test_domain():
    app = flask.Flask(__name__)
    b = babel.Babel(app, default_locale="de_DE")
    domain = babel.Domain(domain="test")

    with app.test_request_context():
        assert domain.gettext("first") == "erste"
        assert babel.gettext("first") == "first"


def test_as_default():
    app = flask.Flask(__name__)
    b = babel.Babel(app, default_locale="de_DE")
    domain = babel.Domain(domain="test")

    with app.test_request_context():
        assert babel.gettext("first") == "first"
        domain.as_default()
        assert babel.gettext("first") == "erste"


def test_default_domain():
    app = flask.Flask(__name__)
    b = babel.Babel(app, default_locale="de_DE", default_domain="test")

    with app.test_request_context():
        assert babel.gettext("first") == "erste"


def test_multiple_apps():
    app1 = flask.Flask(__name__)
    b1 = babel.Babel(app1, default_locale="de_DE")

    app2 = flask.Flask(__name__)
    b2 = babel.Babel(app2, default_locale="de_DE")

    with app1.test_request_context() as ctx:
        assert babel.gettext("Yes") == "Ja"

        assert ("de_DE", "messages") in b1.domain_instance.get_translations_cache(ctx)

    with app2.test_request_context() as ctx:
        assert "de_DE", "messages" not in b2.domain_instance.get_translations_cache(ctx)


def test_cache(mocker):
    load_mock = mocker.patch(
        "babel.support.Translations.load", side_effect=babel.support.Translations.load
    )

    app = flask.Flask(__name__)
    b = babel.Babel(app, default_locale="de_DE", locale_selector=lambda: the_locale)

    # first request, should load en_US
    the_locale = "en_US"
    with app.test_request_context() as ctx:
        assert b.domain_instance.get_translations_cache(ctx) == {}
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 1

    # second request, should use en_US from cache
    with app.test_request_context() as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages")
        }
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 1

    # third request, should load de_DE from cache
    the_locale = "de_DE"
    with app.test_request_context() as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages")
        }
        assert babel.gettext("Yes") == "Ja"
    assert load_mock.call_count == 2

    # now everything is cached, so no more loads should happen!
    the_locale = "en_US"
    with app.test_request_context() as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages"),
            ("de_DE", "messages"),
        }
        assert babel.gettext("Yes") == "Yes"
    assert load_mock.call_count == 2

    the_locale = "de_DE"
    with app.test_request_context() as ctx:
        assert set(b.domain_instance.get_translations_cache(ctx)) == {
            ("en_US", "messages"),
            ("de_DE", "messages"),
        }
        assert babel.gettext("Yes") == "Ja"
    assert load_mock.call_count == 2


def test_plurals():

    app = flask.Flask(__name__)

    def set_locale():
        return flask.request.environ["LANG"]

    babel.Babel(app, locale_selector=set_locale)

    # Plural-Forms: nplurals=2; plural=(n != 1)
    with app.test_request_context(environ_overrides={"LANG": "de_DE"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "1 Apfel"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "2 Äpfel"

    # Plural-Forms: nplurals=1; plural=0;
    with app.test_request_context(environ_overrides={"LANG": "ja"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "リンゴ 1 個"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "リンゴ 2 個"


def test_plurals_different_domains():

    app = flask.Flask(__name__)

    app.config.update(
        {
            "BABEL_TRANSLATION_DIRECTORIES": ";".join(
                (
                    "translations",
                    "translations_different_domain",
                )
            ),
            "BABEL_DOMAIN": ";".join(
                (
                    "messages",
                    "myapp",
                )
            ),
        }
    )

    def set_locale():
        return flask.request.environ["LANG"]

    babel.Babel(app, locale_selector=set_locale)

    # Plural-Forms: nplurals=2; plural=(n != 1)
    with app.test_request_context(environ_overrides={"LANG": "de_DE"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "1 Apfel"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "2 Äpfel"

    # Plural-Forms: nplurals=1; plural=0;
    with app.test_request_context(environ_overrides={"LANG": "ja"}):

        assert ngettext("%(num)s Apple", "%(num)s Apples", 1) == "リンゴ 1 個"
        assert ngettext("%(num)s Apple", "%(num)s Apples", 2) == "リンゴ 2 個"
