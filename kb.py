#!/usr/bin/env python3

from kickbase_api.kickbase import Kickbase
import numpy as np
from rich import print as rprint
from typing import Union
from kickbase_api.models.league_data import LeagueData
from kickbase_api.models.player import Player
from kickbase_api.models.market_player import MarketPlayer
import click


class KickbaseCL(Kickbase):

    def _extract_player_stats(self, days: int, league: Union[str, LeagueData], player: Union[Player, MarketPlayer]):
        name = f"{player.first_name} {player.last_name}"
        stats = self.league_user_player_stats(league, player)
        market_values = np.array([d['m'] for d in stats.market_values]) / 1.0e6
        buy_price = getattr(stats, "buyPrice", None)
        eta_h = player.expiry // 3600 if hasattr(player, "expiry") else None
        eta_mins = int(60*(player.expiry / 3600 - eta_h)) if eta_h is not None else None
        # Marktwertentwicklung der letzten Tage (in Tausend €):
        vals = np.ceil(1e3*(market_values[-days:] - market_values[-days-1:-1]))
        # Trendstring der Marktwertentwicklung zur Ausgabe
        trendstr = "".join(f"[green]↑{x:3.0f}T " if x >=
                           0.0 else f"[red]↓{-x:3.0f}T " for x in vals)
        return name, buy_price, market_values, vals, trendstr, eta_h, eta_mins

    def print_team_stats(self, days: int = 3, only_increasing: bool = False):
        for league in self.leagues():
            print(f"Liga: {league.name}")
            for player in self.league_user_players(league, self.user):
                name, buy_price, market_values, vals, trendstr, _, _ = self._extract_player_stats(days,
                                                                                                  league, player)
                # Falls Spieler aktuell im MW fällt, ignoriere ihn
                if only_increasing and vals[-1] < 0.0:
                    continue
                # Gewinn / Verlust seit Kauf des Spielers?
                gewinn = np.abs(1e-6*buy_price - market_values[-1])
                g_sign = "[red]↓" if gewinn < 0.0 else "[green]↑"
                # Ausgabe
                rstr = f"{trendstr} [white]({g_sign}{gewinn:5.2f} [white]Mio | " \
                    + f"{market_values[-1]: 4.1f} Mio MW | " \
                    + f"{player.totalPoints:4d}P | " \
                    + f"Ø {player.averagePoints:3d}P) {name} "
                rprint(rstr)
            print("")

    def print_market_stats(self, days: int = 3, only_increasing: bool = False):
        for league in self.leagues():
            print(f"Liga: {league.name}")
            # Nur Spieler, die noch niemandem gehören:
            players = [p for p in self.market(league).players if not p.user_id]
            for player in players:
                name, _, market_values, vals, trendstr, eta_h, eta_mins = self._extract_player_stats(days,
                                                                                                     league, player)
                # Falls Spieler aktuell im MW fällt, ignoriere ihn
                if only_increasing and vals[-1] < 0.0:
                    continue
                # Ausgabe
                rstr = f"{trendstr} [white](MW: {market_values[-1]:4.1f} Mio | " \
                    + f"{player.totalPoints:4d}P | " \
                    + f"Ø {player.averagePoints:3d}P | " \
                    + f"{eta_h:2}:{eta_mins:02d}h) {name}"
                rprint(rstr)
            print("")

    def print_live_matchday_punkte(self):
        for league in self.leagues():
            r = self._do_get("/leagues/{}/live/".format(league.id), True)
            res = []
            for player in r.json()['u'][2]['pl']:
                name = player['n']
                pkte = player['t']
                res += [{'name': name, 'punkte': pkte}]
            d = sorted(res, key=lambda i: i['punkte'], reverse=True)
            for p in d:
                print(f"{p['punkte']:3d} {p['name']}")
            print("---------------------------------")
            print(sum(p['punkte'] for p in d), end="\n\n")


@click.command()
@click.option("--market", is_flag=True, help="Ausgabe des Transfermarkts aller Ligen der letzten 3 Tage")
@click.option("--team", is_flag=True, help="Ausgabe des eigenen Teams aller Ligen der letzten 3 Tage")
@click.option("--only_increasing", is_flag=True, help="Ignoriere alle Spieler, deren MW aktuell fällt")
@click.option("--matchday", is_flag=True, help="Ausgabe der Livepunkte des eigenen Teams während des Spieltags")
def cli(*args, **kwargs):
    """ Extrem simples Kickbase CLI. (Leider ohne Lewandowskicheat) """
    kb = KickbaseCL()
    kb.login("deine_login_mail", "dein_pw")
    if kwargs["market"]:
        kb.print_market_stats(only_increasing=kwargs['only_increasing'])
    if kwargs["team"]:
        kb.print_team_stats(only_increasing=kwargs['only_increasing'])
    if kwargs["matchday"]:
        kb.print_live_matchday_punkte()


if __name__ == '__main__':
    cli()
