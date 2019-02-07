from NeuroMLUtilities import ConnectionInfo
import PyOpenWorm as P
from PyOpenWorm.worm import Worm
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.context import Context
from PyOpenWorm.connection import Connection

import logging

############################################################

#   A simple script to read the values in PyOpenWorm
#   Originally written by Mark Watts (github.com/mwatts15)

############################################################

logger = logging.getLogger("OpenWormReader")


class OpenWormReader:
    def __init__(self):
        logger.info("Initialising OpenWormReader")
        P.connect(configFile='.pow/pow.conf')
        logger.info("Finished initialising OpenWormReader")

    def readDataFromSpreadsheet(self, *IGNORED_args, **IGNORED_kwargs):
        conns = []
        cells = []

        ctx = Context(ident='http://openworm.org/data')
        net = Worm().neuron_network()
        c = ctx.stored(Connection)()
        net.synapse(c)
        c.post_cell(Neuron())
        for s in c.load():
            pre = str(s.pre_cell().name())
            post = str(s.post_cell().name())

            if isinstance(s.post_cell(), Neuron):
                syntype = str(s.syntype())
                syntype = syntype[0].upper() + syntype[1:]
                num = int(s.number())
                synclass = str(s.synclass())
                ci = ConnectionInfo(pre, post, num, syntype, synclass)
                conns.append(ci)
                if pre not in cells:
                    cells.append(pre)
                if post not in cells:
                    cells.append(post)

        logger.info("Total cells read " + str(len(cells)))
        logger.info("Total connections read " + str(len(conns)))
        P.disconnect()
        return cells, conns


if __name__ == "__main__":
    from UpdatedSpreadsheetDataReader import readDataFromSpreadsheet

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(name)s - %(levelname)s: %(message)s')
    owr = OpenWormReader()

    cells, conns = owr.readDataFromSpreadsheet()

    print("%i cells in OpenWormReader: %s..." % (len(cells), ", ".join(sorted(cells)[0:3])))

    print("Found %s connections: %s..." % (len(conns), conns[0]))
    pow_conns_map = {}
    for c in conns:
        pow_conns_map[c.short()] = c

    cells2, conns2 = readDataFromSpreadsheet(include_nonconnected_cells=True)

    spreadsheet_conns_map = {}
    for c2 in conns2:
        spreadsheet_conns_map[c2.short()] = c2

    maxn = 3000

    refs = list(pow_conns_map.keys())

    for i in range(min(maxn, len(refs))):
        #print("\n-----  Connection in OWR: %s"%refs[i])
        # print pow_conns_map[refs[i]]
        if refs[i] in spreadsheet_conns_map:
            if pow_conns_map[refs[i]].number != spreadsheet_conns_map[refs[i]].number:
                print("Mismatch: %s != %s" % (pow_conns_map[refs[i]], spreadsheet_conns_map[refs[i]]))
        else:
            print("Spreadsheet reader is missing %s" % pow_conns_map[refs[i]])

    refs = list(spreadsheet_conns_map.keys())

    for i in range(min(maxn, len(refs))):
        #print("\n-----  Connection in USR: %s"%refs[i])
        # print spreadsheet_conns_map[refs[i]]
        if refs[i] in pow_conns_map:
            if pow_conns_map[refs[i]].number != spreadsheet_conns_map[refs[i]].number:
                print("Mismatch: %s != %s" % (pow_conns_map[refs[i]], spreadsheet_conns_map[refs[i]]))
        else:
            print("PyOpenWorm reader is missing %s" % spreadsheet_conns_map[refs[i]])
