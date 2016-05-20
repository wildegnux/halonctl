from six.moves import StringIO
from halonctl.modapi import Formatter

class DiamondFormatter(Formatter):
    def format(self, data, args):
        buf = StringIO()
        if args._mod_name == "stat":
            for j, line in enumerate(data[1:]):
                if j != 0: buf.write("\n")
                stattype = args.key[0]
                if stattype == "hsl:stat":
                    for i, key in enumerate(line[:len(line)-3]):
                        if i != 0: buf.write(".")
                        key = key.replace("-", "_") if i == len(line)-4 else key.replace(":", "-")
                        buf.write(key)
                    buf.write(" {}".format(line[len(line)-3]))
                elif stattype in (
                    "system-mem-usage", "system-swap-usage", "system-storage-usage", "system-storage-latency",
                    "mail-license-count", "mail-queue-count", "mail-quarantine-count"
                ):
                    buf.write("{}.{} {}".format(line[0], stattype.replace("-", "_"), line[1]))
                else:
                    for i, key in enumerate(line[1:]):
                        if i != 0: buf.write("\n")
                        name = data[0][i+1].replace("-", "_")
                        buf.write("{}.{}.{} {}".format(line[0], stattype, name, key))
        return buf.getvalue()

formatter = DiamondFormatter()
