from __future__ import annotations

from typing import TYPE_CHECKING

from plextraktsync.factory import logging
from plextraktsync.trakt.TraktUserListCollection import TraktUserListCollection

if TYPE_CHECKING:
    from plextraktsync.config.SyncConfig import SyncConfig
    from plextraktsync.plan.Walker import Walker
    from plextraktsync.plex.PlexApi import PlexApi
    from plextraktsync.trakt.TraktApi import TraktApi


class Sync:
    logger = logging.getLogger(__name__)

    def __init__(self, config: SyncConfig, plex: PlexApi, trakt: TraktApi):
        self.config = config
        self.plex = plex
        self.trakt = trakt
        self.walker = None

    def sync(self, walker: Walker, dry_run=False):
        self.walker = walker
        trakt_lists = TraktUserListCollection()
        is_partial = walker.is_partial and not dry_run

        from plextraktsync.sync.plugin import SyncPluginManager
        pm = SyncPluginManager()
        pm.register_plugins(self)

        pm.hook.init(sync=self, trakt_lists=trakt_lists, is_partial=is_partial, dry_run=dry_run)

        if self.config.need_library_walk:
            for movie in walker.find_movies():
                pm.hook.walk_movie(movie=movie, dry_run=dry_run)

            for episode in walker.find_episodes():
                pm.hook.walk_episode(episode=episode, dry_run=dry_run)

        pm.hook.fini(walker=walker, trakt_lists=trakt_lists, dry_run=dry_run)
