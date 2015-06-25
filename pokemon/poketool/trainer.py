
from generic import Editable
from util import BinaryIO


class TrainerPokemon(Editable):
    def define(self, trainer):
        self.trainer = trainer
        self.uint8('ai')
        self.uint8('pad0', width=1)
        self.uint8('opposite_gender', width=1)
        self.uint8('pad1', width=3)
        self.uint8('ability', width=1)
        self.uint16('level')
        self.uint16('natid', width=10)
        self.uint16('forme', width=6)
        self.moves = []
        self.attribute('moves')
        self.item = 0
        self.attribute('item')
        if self.trainer.game.is_hgss():
            self.seal_capsule = 0
            self.attribute('seal_capsule')

    def load(self, reader):
        Editable.load(self, reader)
        if self.trainer.hold_items:
            self.item = reader.readUInt16()
        if self.trainer.movesets:
            self.moves = [reader.readUInt16() for i in range(4)]
        if self.trainer.game.is_hgss():
            self.seal_capsule = reader.readUInt16()
        return self

    def save(self, writer):
        writer = Editable.save(writer)
        if self.trainer.hold_items:
            writer.writeUInt16(self.item)
        if self.trainer.movesets:
            for move in self.moves:
                writer.writeUInt16(move)
        if self.trainer.game.is_hgss():
            writer.writeUInt16(self.seal_capsule)
        return writer


class Trainer(Editable):
    def define(self, game):
        self.game = game
        self.uint8('movesets', width=1)
        self.uint8('hold_items', width=1)
        self.uint8('pad0', width=6)
        self.uint8('class')
        self.uint8('battle_type')
        self.uint8('num_pokemon')
        self.array('items', self.uint16, length=4)
        self.uint32('ai')
        self.uint8('battle_type2')
        self.pokemon = None

    def load_pokemon(self, reader):
        reader = BinaryIO.reader(reader)
        self.pokemon = []
        for i in range(self.num_pokemon):
            self.pokemon.append(TrainerPokemon(self, reader=reader))

    def save(self, writer):
        self.update()
        return Editable.save(writer)

    def save_pokemon(self, writer):
        self.update()
        for poke in self.pokemon:
            writer = poke.save(writer)
        return writer

    def update(self):
        if self.pokemon is not None:
            self.num_pokemon = len(self.pokemon)
            for poke in self.pokemon:
                if any(poke.moves):
                    self.movesets = 1
                    break
            else:
                self.movesets = 0
            for poke in self.pokemon:
                if poke.item:
                    self.hold_items = 1
                    break
            else:
                self.hold_items = 0


def main(argv):
    import json

    from pokemon import Game

    try:
        game = Game.from_workspace(argv[1])
        command = argv[2].lower()
        if command == '--import':
            handle = open(argv[4])
        elif command == '--export':
            handle = open(argv[4], 'w')
        else:
            raise ValueError
        trainer_id = argv[3].lower()
        if trainer_id != 'all':
            trainer_id = int(trainer_id)
    except Exception as e:
        print('Usage: {0} <workspace> (--import|--export) <id|ALL> <file.json>'
              .format(argv[0]))
        return 1
    trainer_archive = game.trainer_archive
    trainer_pokemon_archive = game.trainer_pokemon_archive
    if command == '--export':
        if trainer_id == 'all':
            trainer_ids = range(trainer_archive.fatb.num)
        else:
            trainer_ids = [trainer_id]
        out = []
        for trainer_id in trainer_ids:
            trainer = Trainer(game, reader=trainer_archive.files[trainer_id])
            trainer.load_pokemon(trainer_pokemon_archive.files[trainer_id])
            tr_dict = trainer.to_dict()
            tr_dict['pokemon'] = [tr_poke.to_dict()
                                  for tr_poke in trainer.pokemon]
            out.append(tr_dict)
        handle.write(json.dumps(out, sort_keys=True, indent=4))
    else:
        data = json.load(handle)
        if trainer_id == 'all':
            trainer_ids = len(data)
        else:
            trainer_ids = [trainer_id]
        for trainer_id in trainer_ids:
            tr_dict = data.pop(0)
            trainer = Trainer(game)
            trainer.from_dict(tr_dict)
            trainer.pokemon = [TrainerPokemon(trainer).from_dict(poke_dict)
                               for poke_dict in tr_dict['pokemon']]
            tr_writer = trainer.save()
            p_writer = trainer.save_pokemon()
            try:
                trainer_archive.files[trainer_id] = tr_writer.getvalue()
                trainer_pokemon_archive.files[trainer_id] = p_writer.getvalue()
            except:
                trainer_archive.add(data=tr_writer.getvalue())
                trainer_pokemon_archive.add(data=p_writer.getvalue())
        game.save_archive(trainer_archive, game.trainer_archive_file)
        game.save_archive(trainer_pokemon_archive,
                          game.trainer_pokemon_archive_file)
    handle.close()


if __name__ == '__main__':
    import sys

    exit(main(sys.argv))
