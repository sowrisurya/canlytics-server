
HEX_MAP = {
	"0": "P0",
	"1": "P1",
	"2": "P2",
	"3": "P3",
	"4": "C0",
	"5": "C1",
	"6": "C2",
	"7": "C3",
	"8": "B0",
	"9": "B1",
	"A": "B2",
	"B": "B3",
	"C": "U0",
	"D": "U1",
	"E": "U2",
	"F": "U3"
}

READ_PARAMS = [
	{
		"param": "Param 1",
		"read": "22 f1 86",
	},
	{
		"param": "Param 2",
		"read": "22 f1 90",
	},
	{
		"param": "Param 3",
		"read": "22 f1 88",
	},
	{
		"param": "Param 4",
		"read": "22 f1 8c",
	},
	{
		"param": "Param 5",
		"read": "22 f1 24",
	},
	{
		"param": "Param 6",
		"read": "22 f1 25",
	},
	{
		"param": "Param 7",
		"read": "22 f1 11",
	},
	{
		"param": "Param 8",
		"read": "22 f1 12",
	},
	{
		"param": "Param 9",
        "read": "22 f1 13",	
	},
	{
		"param": "Param 10",
		"read": "22 f1 08",
	},
	{
		"param": "Param 11",
		"read": "22 f1 20",
	},
	{
		"param": "Param 12",
		"read": "22 f1 80",
	},
	{
		"param": "Param 13",
		"read": "22 f1 03",
	},
	{
		"param": "Param 14",
		"read": "22 dd 00",
	},
	{
		"param": "Param 15",
		"read": "22 dd 01",
	},
	{
		"param": "Param 16",
		"read": "22 f1 70",
	},
	{
		"param": "Param 17",
		"read": "01 02",
	}
]

with open("data/DTC_CODES.csv", "r") as f:
	DTC_CODES = {
		_[0]: _[1]
		for _ in [_.split(",") for _ in f.read().split("\n") if _]
	}

with open("data/FAULT_TYPES.csv", "r") as f:
	FAULT_TYPES = {
		_[0]: _[1]
		for _ in [_.split(",") for _ in f.read().split("\n") if _]
	}

with open("data/NRC_CODES.csv", "r") as f:
	NRC_CODES = {
		_[0]: _[1]
		for _ in [_.split(",") for _ in f.read().split("\n") if _]
	}
