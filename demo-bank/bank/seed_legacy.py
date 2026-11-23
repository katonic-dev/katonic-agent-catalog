"""Seed data, part 11: an old core banking system, read only. Tables with cryptic names, stored procedures and four batch programs.

This estate is separate from the current core system. Its customers and account numbers are its own and are not the same records.
Three things are worked out from the text and the sample rows: the meaning of most columns, the codes, and the scale of amounts.
One column, AC_X1, is not read or written anywhere and its sample values show no pattern. Its meaning cannot be worked out.
One program, INTACCR, has a rounding rule that a conversion must keep (rule FIN-14).
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, ROUND_DOWN

from .seed_base import d_ago


def jul(d: date) -> int:
    return d.year * 1000 + d.timetuple().tm_yday


def ymd(d: date) -> int:
    return d.year * 10000 + d.month * 100 + d.day


RATE_BP = {"R01": 25, "R02": 125, "R03": 325, "R04": 450, "ROD": 1190, "RUN": 2490}


def daily_interest(bal_cents: int, rate_cd: str) -> Decimal:
    """One day of interest by rule FIN-14: balance in units, times the rate, over 365, truncated at six decimals."""
    units = Decimal(bal_cents) / Decimal(100)
    return (units * (Decimal(RATE_BP[rate_cd]) / Decimal(10000)) / Decimal(365)).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)


def accrued(today: date, status: str, bal: int, rt: str, flg1: str) -> float:
    if status != "A":
        return 0.0
    code = rt if bal >= 0 else ("ROD" if flg1 == "Y" else "RUN")
    return float(daily_interest(bal, code) * (today.day - 1))


def col(name, typ, comment="", nullable="N"):
    return {"name": name, "type": typ, "nullable": nullable, "catalogue_comment": comment}


def build_tables(today: date) -> dict:
    t = {}
    t["CUMAST"] = {
        "table_name": "CUMAST", "row_count": 214806, "primary_key": ["CU_NO"], "foreign_keys": [], "indexes": ["CUMAST_X1 (CU_NM)"],
        "catalogue_comment": "",
        "columns": [col("CU_NO", "CHAR(8)", "Customer number"), col("CU_NM", "CHAR(40)", "Name"),
                    col("CU_SG", "CHAR(1)"), col("CU_OPN", "DECIMAL(8,0)"), col("CU_ST", "CHAR(1)")],
        "sample_rows": [
            {"CU_NO": "00417731", "CU_NM": "ASHGROVE, LUCINDA M", "CU_SG": "R", "CU_OPN": ymd(today - timedelta(days=4100)), "CU_ST": "A"},
            {"CU_NO": "00417802", "CU_NM": "FERNHOLLOW DRAINAGE LTD", "CU_SG": "B", "CU_OPN": ymd(today - timedelta(days=3650)), "CU_ST": "A"},
            {"CU_NO": "00418115", "CU_NM": "BRAMBLEWICK, TORIN", "CU_SG": "P", "CU_OPN": ymd(today - timedelta(days=5200)), "CU_ST": "A"},
            {"CU_NO": "00419240", "CU_NM": "OSTERLEY, HANNELORE", "CU_SG": "R", "CU_OPN": ymd(today - timedelta(days=2900)), "CU_ST": "A"},
            {"CU_NO": "00420068", "CU_NM": "WILLOWMERE PRINT AND SIGN LTD", "CU_SG": "B", "CU_OPN": ymd(today - timedelta(days=2100)), "CU_ST": "A"},
            {"CU_NO": "00421377", "CU_NM": "DENNICOTT, ROWAN", "CU_SG": "R", "CU_OPN": ymd(today - timedelta(days=6400)), "CU_ST": "C"}]}
    acc = [  # AC_NO, CU_NO, TY, ST, BAL(cents), ACR, RT, LTX days ago, FLG1, FLG2, X1
        ("4410007731", "00417731", "10", "A", 1234567, None, "R01", 3, "Y", "E", 0),
        ("4410007732", "00417731", "20", "A", 8800000, None, "R03", 9, "N", "E", 0),
        ("4410008102", "00417802", "30", "A", -250075, None, "R02", 1, "Y", "P", 12),
        ("4410008115", "00418115", "20", "A", 45123390, None, "R04", 9, "N", "P", 0),
        ("4410009240", "00419240", "10", "D", 18420, None, "R01", 900, "N", "P", 7),
        ("4410009241", "00419240", "20", "A", 150000, None, "R03", 200, "N", "E", 0),
        ("4410010068", "00420068", "30", "A", 3299999, None, "R02", 2, "N", "P", 3),
        ("4410011377", "00421377", "10", "C", 0, None, "R01", 1300, "N", "P", 0)]
    t["ACMAST"] = {
        "table_name": "ACMAST", "row_count": 305992, "primary_key": ["AC_NO"], "foreign_keys": [{"column": "CU_NO", "references": "CUMAST.CU_NO"},
                                                                                              {"column": "AC_RT", "references": "RTTAB.RT_CD"}],
        "indexes": ["ACMAST_X1 (CU_NO)", "ACMAST_X2 (AC_ST, AC_LTX)"], "catalogue_comment": "",
        "columns": [col("AC_NO", "CHAR(10)", "Account number"), col("CU_NO", "CHAR(8)", "Customer number"), col("AC_TY", "CHAR(2)"),
                    col("AC_ST", "CHAR(1)"), col("AC_BAL", "DECIMAL(15,0)"), col("AC_ACR", "DECIMAL(15,6)"), col("AC_RT", "CHAR(3)"),
                    col("AC_LTX", "DECIMAL(7,0)"), col("AC_FLG1", "CHAR(1)"), col("AC_FLG2", "CHAR(1)"), col("AC_X1", "DECIMAL(3,0)", nullable="Y")],
        "sample_rows": [{"AC_NO": a, "CU_NO": c, "AC_TY": ty, "AC_ST": s, "AC_BAL": b, "AC_ACR": accrued(today, s, b, rt, f1), "AC_RT": rt, "AC_LTX": jul(today - timedelta(days=ago)),
                         "AC_FLG1": f1, "AC_FLG2": f2, "AC_X1": x1} for a, c, ty, s, b, acr, rt, ago, f1, f2, x1 in acc]}
    tx = [("TX0099120001", "4410007731", 3, "101", 150000, "C", "CASH DEP BRANCH 04"), ("TX0099120002", "4410007731", 3, "401", 42000, "D", "SO 000771"),
          ("TX0099120003", "4410007731", 12, "201", 8000, "D", "ATM 0412"), ("TX0099120004", "4410007731", 30, "301", 307, "C", "INT"),
          ("TX0099120005", "4410008102", 1, "102", 120000, "C", "CHQ 000231"), ("TX0099120006", "4410008102", 0, "302", 1500, "D", "OD FEE"),
          ("TX0099120007", "4410008115", 9, "402", 500000, "D", "TFR 4410007732"), ("TX0099120008", "4410007732", 9, "402", 500000, "C", "TFR 4410008115")]
    t["TXHIST"] = {
        "table_name": "TXHIST", "row_count": 48114220, "primary_key": ["TX_ID"], "foreign_keys": [{"column": "AC_NO", "references": "ACMAST.AC_NO"}],
        "indexes": ["TXHIST_X1 (AC_NO, TX_DT)"], "catalogue_comment": "",
        "columns": [col("TX_ID", "CHAR(12)"), col("AC_NO", "CHAR(10)", "Account number"), col("TX_DT", "DECIMAL(8,0)"), col("TX_CD", "CHAR(3)"),
                    col("TX_AM", "DECIMAL(13,0)"), col("TX_SN", "CHAR(1)"), col("TX_RF", "CHAR(20)", "Reference")],
        "sample_rows": [{"TX_ID": i, "AC_NO": a, "TX_DT": ymd(today - timedelta(days=ago)), "TX_CD": c, "TX_AM": am, "TX_SN": sn, "TX_RF": rf}
                        for i, a, ago, c, am, sn, rf in tx]}
    t["RTTAB"] = {
        "table_name": "RTTAB", "row_count": 14, "primary_key": ["RT_CD"], "foreign_keys": [], "indexes": [], "catalogue_comment": "",
        "columns": [col("RT_CD", "CHAR(3)"), col("RT_BP", "DECIMAL(5,0)"), col("RT_FR", "DECIMAL(8,0)")],
        "sample_rows": [{"RT_CD": "R01", "RT_BP": 25, "RT_FR": ymd(today - timedelta(days=700))}, {"RT_CD": "R02", "RT_BP": 125, "RT_FR": ymd(today - timedelta(days=700))},
                        {"RT_CD": "R03", "RT_BP": 325, "RT_FR": ymd(today - timedelta(days=300))}, {"RT_CD": "R04", "RT_BP": 450, "RT_FR": ymd(today - timedelta(days=300))},
                        {"RT_CD": "ROD", "RT_BP": 1190, "RT_FR": ymd(today - timedelta(days=700))}, {"RT_CD": "RUN", "RT_BP": 2490, "RT_FR": ymd(today - timedelta(days=700))}]}
    t["SOMAST"] = {
        "table_name": "SOMAST", "row_count": 18441, "primary_key": ["SO_ID"], "foreign_keys": [{"column": "AC_NO", "references": "ACMAST.AC_NO"}],
        "indexes": ["SOMAST_X1 (SO_ST, SO_ND)"], "catalogue_comment": "",
        "columns": [col("SO_ID", "CHAR(8)"), col("AC_NO", "CHAR(10)", "Account number"), col("SO_BEN", "CHAR(10)"), col("SO_AM", "DECIMAL(13,0)"),
                    col("SO_FQ", "CHAR(1)"), col("SO_ND", "DECIMAL(8,0)"), col("SO_ST", "CHAR(1)")],
        "sample_rows": [{"SO_ID": "SO000771", "AC_NO": "4410007731", "SO_BEN": "4410030011", "SO_AM": 42000, "SO_FQ": "M", "SO_ND": ymd(today + timedelta(days=11)), "SO_ST": "A"},
                        {"SO_ID": "SO000802", "AC_NO": "4410008102", "SO_BEN": "4410044120", "SO_AM": 15000, "SO_FQ": "W", "SO_ND": ymd(today), "SO_ST": "A"},
                        {"SO_ID": "SO000917", "AC_NO": "4410008115", "SO_BEN": "4410051188", "SO_AM": 900000, "SO_FQ": "Q", "SO_ND": ymd(today + timedelta(days=40)), "SO_ST": "A"},
                        {"SO_ID": "SO000950", "AC_NO": "4410010068", "SO_BEN": "4410060042", "SO_AM": 250000, "SO_FQ": "M", "SO_ND": ymd(today + timedelta(days=6)), "SO_ST": "S"}]}
    t["DRMLOG"] = {
        "table_name": "DRMLOG", "row_count": 9030, "primary_key": ["DM_AC", "DM_DT"], "foreign_keys": [{"column": "DM_AC", "references": "ACMAST.AC_NO"}],
        "indexes": [], "catalogue_comment": "",
        "columns": [col("DM_AC", "CHAR(10)"), col("DM_DT", "DECIMAL(8,0)"), col("DM_FG", "CHAR(1)")],
        "sample_rows": [{"DM_AC": "4410009240", "DM_DT": ymd(today - timedelta(days=120)), "DM_FG": "S"},
                        {"DM_AC": "4410002215", "DM_DT": ymd(today - timedelta(days=400)), "DM_FG": "S"},
                        {"DM_AC": "4410002215", "DM_DT": ymd(today - timedelta(days=95)), "DM_FG": "R"}]}
    return t


PROCEDURES = {
    "SP_POST_TXN": {
        "parameters": [("p_ac", "CHAR(10)"), ("p_cd", "CHAR(3)"), ("p_am", "DECIMAL(13,0)"), ("p_sn", "CHAR(1)"), ("p_rf", "CHAR(20)")],
        "last_changed_days_ago": 880,
        "source": """CREATE PROCEDURE SP_POST_TXN (p_ac CHAR(10), p_cd CHAR(3), p_am DECIMAL(13,0), p_sn CHAR(1), p_rf CHAR(20))
-- Posts one transaction to one account. Amounts arrive in the smallest unit.
BEGIN
  DECLARE v_st CHAR(1);
  DECLARE v_bal DECIMAL(15,0);
  DECLARE v_id CHAR(12);

  SELECT AC_ST, AC_BAL INTO v_st, v_bal FROM ACMAST WHERE AC_NO = p_ac FOR UPDATE;

  -- closed and frozen accounts take nothing
  IF v_st IN ('C', 'F') THEN
    SIGNAL SQLSTATE '75001' SET MESSAGE_TEXT = 'ACCOUNT NOT OPEN FOR POSTING';
  END IF;

  IF p_sn NOT IN ('C', 'D') THEN
    SIGNAL SQLSTATE '75002' SET MESSAGE_TEXT = 'BAD SIGN';
  END IF;

  IF p_sn = 'C' THEN
    UPDATE ACMAST SET AC_BAL = AC_BAL + p_am WHERE AC_NO = p_ac;
  ELSE
    UPDATE ACMAST SET AC_BAL = AC_BAL - p_am WHERE AC_NO = p_ac;
  END IF;

  SET v_id = NEXT_TX_ID();
  INSERT INTO TXHIST (TX_ID, AC_NO, TX_DT, TX_CD, TX_AM, TX_SN, TX_RF)
  VALUES (v_id, p_ac, CURRENT_YYYYMMDD(), p_cd, p_am, p_sn, p_rf);

  -- codes 101 102 201 401 402 start with the customer. 301 (interest) and 302 (fee) start with the bank.
  IF p_cd IN ('101', '102', '201', '401', '402') THEN
    UPDATE ACMAST SET AC_LTX = CURRENT_YYYYDDD() WHERE AC_NO = p_ac;
  END IF;

  -- a posting to a dormant account wakes it up, if the customer started it
  IF v_st = 'D' AND p_cd IN ('101', '102', '201', '401', '402') THEN
    UPDATE ACMAST SET AC_ST = 'A' WHERE AC_NO = p_ac;
    INSERT INTO DRMLOG (DM_AC, DM_DT, DM_FG) VALUES (p_ac, CURRENT_YYYYMMDD(), 'R');
  END IF;
END;""",
    },
    "SP_BAL_ENQ": {
        "parameters": [("p_ac", "CHAR(10)")], "last_changed_days_ago": 1500,
        "source": """CREATE PROCEDURE SP_BAL_ENQ (p_ac CHAR(10))
-- Balance enquiry for the branch screen and the phone line.
BEGIN
  DECLARE v_bal DECIMAL(15,0);
  DECLARE v_st CHAR(1);
  DECLARE v_ty CHAR(2);

  SELECT AC_BAL, AC_ST, AC_TY INTO v_bal, v_st, v_ty FROM ACMAST WHERE AC_NO = p_ac;

  IF v_st = 'C' THEN
    RETURN 'CLOSED';
  END IF;

  -- the screen shows pounds and pence style, two decimals
  RETURN CAST(v_bal / 100 AS DECIMAL(13,2));
END;""",
    },
    "SP_RATE_FOR_ACCOUNT": {
        "parameters": [("p_ac", "CHAR(10)")], "last_changed_days_ago": 1210,
        "source": """CREATE PROCEDURE SP_RATE_FOR_ACCOUNT (p_ac CHAR(10))
-- Returns the rate code that applies to an account today.
BEGIN
  DECLARE v_bal DECIMAL(15,0);
  DECLARE v_f1 CHAR(1);
  DECLARE v_rt CHAR(3);

  SELECT AC_BAL, AC_FLG1, AC_RT INTO v_bal, v_f1, v_rt FROM ACMAST WHERE AC_NO = p_ac;

  IF v_bal < 0 THEN
    -- overdrawn: the agreed rate if the customer has an arrangement, else the higher rate
    IF v_f1 = 'Y' THEN
      RETURN 'ROD';
    ELSE
      RETURN 'RUN';
    END IF;
  END IF;

  RETURN v_rt;
END;""",
    },
    "SP_FLAG_DORMANT": {
        "parameters": [("p_ac", "CHAR(10)")], "last_changed_days_ago": 640,
        "source": """CREATE PROCEDURE SP_FLAG_DORMANT (p_ac CHAR(10))
-- Marks one account dormant. Called by the dormant sweep and by branch staff.
BEGIN
  DECLARE v_st CHAR(1);
  DECLARE v_ty CHAR(2);

  SELECT AC_ST, AC_TY INTO v_st, v_ty FROM ACMAST WHERE AC_NO = p_ac FOR UPDATE;

  IF v_st <> 'A' THEN
    RETURN;
  END IF;

  -- term deposits are never made dormant
  IF v_ty = '40' THEN
    RETURN;
  END IF;

  UPDATE ACMAST SET AC_ST = 'D' WHERE AC_NO = p_ac;
  INSERT INTO DRMLOG (DM_AC, DM_DT, DM_FG) VALUES (p_ac, CURRENT_YYYYMMDD(), 'S');
END;""",
    },
    "SP_NEXT_SO_DATE": {
        "parameters": [("p_nd", "DECIMAL(8,0)"), ("p_fq", "CHAR(1)")], "last_changed_days_ago": 410,
        "source": """CREATE PROCEDURE SP_NEXT_SO_DATE (p_nd DECIMAL(8,0), p_fq CHAR(1))
-- Next due date of a standing order after the one just run.
BEGIN
  DECLARE v_d DATE;
  DECLARE v_next DATE;

  SET v_d = TO_DATE(p_nd, 'YYYYMMDD');

  IF p_fq = 'W' THEN
    SET v_next = v_d + 7 DAYS;
  ELSEIF p_fq = 'M' THEN
    SET v_next = ADD_MONTHS(v_d, 1);
  ELSEIF p_fq = 'Q' THEN
    SET v_next = ADD_MONTHS(v_d, 3);
  ELSE
    SIGNAL SQLSTATE '75010' SET MESSAGE_TEXT = 'BAD FREQUENCY';
  END IF;

  -- ADD_MONTHS gives the last day of the month when the day does not exist (31 Jan gives 28 Feb).
  -- The original day is not restored afterwards. See SORUN.
  RETURN TO_YYYYMMDD(v_next);
END;""",
    },
}

INTACCR = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTACCR.
      *---------------------------------------------------------------
      * NIGHTLY INTEREST ACCRUAL. ONE PASS OVER ACMAST.
      * EVERY OPEN ACCOUNT EARNS (OR PAYS) ONE DAY OF INTEREST.
      * ON THE LAST CALENDAR DAY OF THE MONTH THE ACCRUED AMOUNT IS
      * POSTED TO THE ACCOUNT AND THE POSTED PART IS CLEARED.
      *
      * RULE FIN-14 (DO NOT CHANGE WITHOUT FINANCE SIGN-OFF)
      *   DAILY INTEREST IS TRUNCATED AT SIX DECIMALS. IT IS NOT
      *   ROUNDED. THERE IS NO ROUNDED PHRASE ON PURPOSE.
      *   AT MONTH END THE ACCRUED TOTAL IS ROUNDED TO TWO DECIMALS,
      *   HALVES AWAY FROM ZERO. WHAT IS LEFT BELOW ONE CENT STAYS
      *   IN AC-ACR AND IS CARRIED INTO NEXT MONTH.
      *   DAY BASIS IS 365 ALWAYS, ALSO IN A LEAP YEAR.
      *---------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACMAST ASSIGN TO ACMAST ORGANIZATION INDEXED
                  ACCESS MODE DYNAMIC RECORD KEY AC-NO.
           SELECT RTTAB  ASSIGN TO RTTAB  ORGANIZATION INDEXED
                  ACCESS MODE RANDOM RECORD KEY RT-CD.
       DATA DIVISION.
       FILE SECTION.
       FD  ACMAST.
       01  AC-REC.
           05 AC-NO        PIC X(10).
           05 CU-NO        PIC X(8).
           05 AC-TY        PIC XX.
           05 AC-ST        PIC X.
           05 AC-BAL       PIC S9(13) COMP-3.
           05 AC-ACR       PIC S9(9)V9(6) COMP-3.
           05 AC-RT        PIC XXX.
           05 AC-FLG1      PIC X.
       FD  RTTAB.
       01  RT-REC.
           05 RT-CD        PIC XXX.
           05 RT-BP        PIC 9(5).
       WORKING-STORAGE SECTION.
       01  WS-TODAY        PIC 9(8).
       01  WS-TOMORROW     PIC 9(8).
       01  WS-MONTH-END    PIC X VALUE 'N'.
       01  WS-EOF          PIC X VALUE 'N'.
       01  WS-RATE-CD      PIC XXX.
       01  WS-BAL-UNITS    PIC S9(11)V99.
       01  WS-RATE         PIC 9V9(6).
       01  WS-DAILY        PIC S9(9)V9(6).
       01  WS-POST         PIC S9(9)V99.
       01  WS-COUNT        PIC 9(7) VALUE 0.
       PROCEDURE DIVISION.
       0000-MAIN.
           ACCEPT WS-TODAY FROM DATE YYYYMMDD
           COMPUTE WS-TOMORROW = FUNCTION DATE-OF-INTEGER
                   (FUNCTION INTEGER-OF-DATE (WS-TODAY) + 1)
           IF WS-TODAY (5:2) NOT = WS-TOMORROW (5:2)
              MOVE 'Y' TO WS-MONTH-END
           END-IF
           OPEN I-O ACMAST
           OPEN INPUT RTTAB
           PERFORM 1000-READ-NEXT
           PERFORM 2000-ONE-ACCOUNT UNTIL WS-EOF = 'Y'
           CLOSE ACMAST RTTAB
           DISPLAY 'INTACCR ACCOUNTS ACCRUED ' WS-COUNT
           STOP RUN.
       1000-READ-NEXT.
           READ ACMAST NEXT RECORD AT END MOVE 'Y' TO WS-EOF.
       2000-ONE-ACCOUNT.
           IF AC-ST = 'A'
              PERFORM 2100-PICK-RATE
              PERFORM 2200-ACCRUE
              IF WS-MONTH-END = 'Y'
                 PERFORM 2300-POST-MONTH-END
              END-IF
              REWRITE AC-REC
              ADD 1 TO WS-COUNT
           END-IF
           PERFORM 1000-READ-NEXT.
       2100-PICK-RATE.
      * OVERDRAWN: AGREED OVERDRAFT PAYS ROD, ANY OTHER OVERDRAFT RUN
           MOVE AC-RT TO WS-RATE-CD
           IF AC-BAL < 0
              IF AC-FLG1 = 'Y'
                 MOVE 'ROD' TO WS-RATE-CD
              ELSE
                 MOVE 'RUN' TO WS-RATE-CD
              END-IF
           END-IF
           MOVE WS-RATE-CD TO RT-CD
           READ RTTAB INVALID KEY
                DISPLAY 'NO RATE ' WS-RATE-CD ' FOR ' AC-NO
                MOVE 0 TO RT-BP
           END-READ
           COMPUTE WS-RATE = RT-BP / 10000.
       2200-ACCRUE.
      * AC-BAL IS HELD IN THE SMALLEST UNIT. DIVIDE BY 100 FIRST.
           COMPUTE WS-BAL-UNITS = AC-BAL / 100
           COMPUTE WS-DAILY = WS-BAL-UNITS * WS-RATE / 365
           ADD WS-DAILY TO AC-ACR.
       2300-POST-MONTH-END.
           COMPUTE WS-POST ROUNDED = AC-ACR
           IF WS-POST NOT = 0
              CALL 'POSTINT' USING AC-NO WS-POST
              SUBTRACT WS-POST FROM AC-ACR
           END-IF.
      * CHANGE LOG
      *   2019-03 ADDED ROD / RUN OVERDRAFT RATES
      *   2021-09 WS-DAILY WIDENED FROM 4 TO 6 DECIMALS (FIN-14)
"""

STMTEXT = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. STMTEXT.
      *---------------------------------------------------------------
      * MONTHLY STATEMENT EXTRACT.
      * READS THE STATEMENT PERIOD FROM THE PARM FILE (FROM, TO).
      * WRITES ONE HEADER, THE DETAIL LINES AND ONE FOOTER PER ACCOUNT
      * TO THE PRINT FILE (PAPER) OR THE E-FILE (ELECTRONIC).
      *---------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT PARM    ASSIGN TO PARM.
           SELECT ACMAST  ASSIGN TO ACMAST ORGANIZATION INDEXED
                  ACCESS MODE DYNAMIC RECORD KEY AC-NO.
           SELECT CUMAST  ASSIGN TO CUMAST ORGANIZATION INDEXED
                  ACCESS MODE RANDOM RECORD KEY CU-NO.
           SELECT TXHIST  ASSIGN TO TXHIST ORGANIZATION INDEXED
                  ACCESS MODE DYNAMIC RECORD KEY TX-ID
                  ALTERNATE RECORD KEY TX-AC-DT WITH DUPLICATES.
           SELECT PRTFILE ASSIGN TO PRTFILE.
           SELECT EFILE   ASSIGN TO EFILE.
       DATA DIVISION.
       FILE SECTION.
       FD  PARM.
       01  PARM-REC.
           05 PM-FROM      PIC 9(8).
           05 PM-TO        PIC 9(8).
       WORKING-STORAGE SECTION.
       01  WS-EOF          PIC X VALUE 'N'.
       01  WS-TX-EOF       PIC X VALUE 'N'.
       01  WS-NET          PIC S9(13).
       01  WS-OPENING      PIC S9(13).
       01  WS-AMT-UNITS    PIC S9(11)V99.
       01  WS-BAL-UNITS    PIC S9(11)V99.
       01  WS-TYPE-NAME    PIC X(20).
       01  WS-TX-NAME      PIC X(22).
       PROCEDURE DIVISION.
       0000-MAIN.
           OPEN INPUT PARM ACMAST CUMAST TXHIST
           OPEN OUTPUT PRTFILE EFILE
           READ PARM
           PERFORM 1000-NEXT-ACCOUNT
           PERFORM 2000-ONE-ACCOUNT UNTIL WS-EOF = 'Y'
           CLOSE PARM ACMAST CUMAST TXHIST PRTFILE EFILE
           STOP RUN.
       1000-NEXT-ACCOUNT.
           READ ACMAST NEXT RECORD AT END MOVE 'Y' TO WS-EOF.
       2000-ONE-ACCOUNT.
      * CLOSED ACCOUNTS GET NO STATEMENT. DORMANT ONES DO.
           IF AC-ST NOT = 'C' AND (AC-FLG2 = 'P' OR AC-FLG2 = 'E')
              MOVE AC-CU TO CU-NO
              READ CUMAST
              PERFORM 2100-TYPE-NAME
              PERFORM 2200-HEADER
              PERFORM 2300-DETAILS
              PERFORM 2400-FOOTER
           END-IF
           PERFORM 1000-NEXT-ACCOUNT.
       2100-TYPE-NAME.
           EVALUATE AC-TY
              WHEN '10' MOVE 'CURRENT ACCOUNT'   TO WS-TYPE-NAME
              WHEN '20' MOVE 'SAVER'             TO WS-TYPE-NAME
              WHEN '30' MOVE 'BUSINESS CURRENT'  TO WS-TYPE-NAME
              WHEN '40' MOVE 'TERM DEPOSIT'      TO WS-TYPE-NAME
              WHEN OTHER MOVE 'ACCOUNT'          TO WS-TYPE-NAME
           END-EVALUATE.
       2200-HEADER.
      * P = PRIORITY BANNER. R AND B GET NO BANNER.
           IF CU-SG = 'P'
              PERFORM 2210-WRITE-BANNER
           END-IF
           PERFORM 2220-WRITE-HEADER-LINE.
       2300-DETAILS.
           MOVE 0 TO WS-NET
           MOVE 'N' TO WS-TX-EOF
           MOVE AC-NO TO TX-AC
           MOVE PM-FROM TO TX-DT
           START TXHIST KEY NOT LESS THAN TX-AC-DT
              INVALID KEY MOVE 'Y' TO WS-TX-EOF
           END-START
           PERFORM 2310-ONE-TX UNTIL WS-TX-EOF = 'Y'.
       2310-ONE-TX.
           READ TXHIST NEXT RECORD AT END MOVE 'Y' TO WS-TX-EOF
           END-READ
           IF WS-TX-EOF = 'N'
              IF TX-AC NOT = AC-NO OR TX-DT > PM-TO
                 MOVE 'Y' TO WS-TX-EOF
              ELSE
                 PERFORM 2320-DECODE-TX
                 COMPUTE WS-AMT-UNITS = TX-AM / 100
                 IF TX-SN = 'D'
                    COMPUTE WS-AMT-UNITS = WS-AMT-UNITS * -1
                    SUBTRACT TX-AM FROM WS-NET
                 ELSE
                    ADD TX-AM TO WS-NET
                 END-IF
                 PERFORM 2330-WRITE-DETAIL
              END-IF
           END-IF.
       2320-DECODE-TX.
           EVALUATE TX-CD
              WHEN '101' MOVE 'CASH DEPOSIT'          TO WS-TX-NAME
              WHEN '102' MOVE 'CHEQUE DEPOSIT'        TO WS-TX-NAME
              WHEN '201' MOVE 'CASH WITHDRAWAL'       TO WS-TX-NAME
              WHEN '301' MOVE 'INTEREST'              TO WS-TX-NAME
              WHEN '302' MOVE 'FEE'                   TO WS-TX-NAME
              WHEN '401' MOVE 'STANDING ORDER'        TO WS-TX-NAME
              WHEN '402' MOVE 'TRANSFER'              TO WS-TX-NAME
              WHEN OTHER MOVE 'OTHER'                 TO WS-TX-NAME
           END-EVALUATE.
       2400-FOOTER.
      * OPENING BALANCE = CLOSING BALANCE MINUS THE NET MOVEMENT
           COMPUTE WS-OPENING = AC-BAL - WS-NET
           COMPUTE WS-BAL-UNITS = AC-BAL / 100
           PERFORM 2410-WRITE-FOOTER-LINE.
"""

DORMSWP = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. DORMSWP.
      *---------------------------------------------------------------
      * DORMANT ACCOUNT SWEEP. RUNS ON THE FIRST OF EACH MONTH.
      * AN ACCOUNT IS DORMANT WHEN THE CUSTOMER HAS NOT STARTED A
      * TRANSACTION FOR 24 MONTHS. INTEREST AND FEES START WITH THE
      * BANK AND DO NOT COUNT. SEE SP_POST_TXN, WHICH ONLY MOVES
      * AC-LTX FOR CUSTOMER CODES.
      * TERM DEPOSITS (TYPE 40) ARE NEVER SWEPT.
      * ACCOUNTS WITH A LIVE STANDING ORDER ARE NEVER SWEPT.
      *---------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACMAST  ASSIGN TO ACMAST ORGANIZATION INDEXED
                  ACCESS MODE DYNAMIC RECORD KEY AC-NO.
           SELECT SOMAST  ASSIGN TO SOMAST ORGANIZATION INDEXED
                  ACCESS MODE DYNAMIC RECORD KEY SO-ID
                  ALTERNATE RECORD KEY SO-AC WITH DUPLICATES.
           SELECT DRMLOG  ASSIGN TO DRMLOG ORGANIZATION SEQUENTIAL.
           SELECT LETTERS ASSIGN TO LETTERS.
       DATA DIVISION.
       FILE SECTION.
       FD  DRMLOG.
       01  DM-REC.
           05 DM-AC        PIC X(10).
           05 DM-DT        PIC 9(8).
           05 DM-FG        PIC X.
       WORKING-STORAGE SECTION.
       01  WS-TODAY        PIC 9(8).
       01  WS-TODAY-INT    PIC 9(7).
       01  WS-LTX-INT      PIC 9(7).
       01  WS-LTX-DATE     PIC 9(8).
       01  WS-DAYS-IDLE    PIC 9(7).
       01  WS-LIMIT-DAYS   PIC 9(4) VALUE 730.
       01  WS-EOF          PIC X VALUE 'N'.
       01  WS-SO-FOUND     PIC X.
       01  WS-SWEPT        PIC 9(7) VALUE 0.
       PROCEDURE DIVISION.
       0000-MAIN.
           ACCEPT WS-TODAY FROM DATE YYYYMMDD
           COMPUTE WS-TODAY-INT = FUNCTION INTEGER-OF-DATE (WS-TODAY)
           OPEN I-O ACMAST
           OPEN INPUT SOMAST
           OPEN EXTEND DRMLOG
           OPEN OUTPUT LETTERS
           PERFORM 1000-READ-NEXT
           PERFORM 2000-ONE-ACCOUNT UNTIL WS-EOF = 'Y'
           CLOSE ACMAST SOMAST DRMLOG LETTERS
           DISPLAY 'DORMSWP ACCOUNTS SWEPT ' WS-SWEPT
           STOP RUN.
       1000-READ-NEXT.
           READ ACMAST NEXT RECORD AT END MOVE 'Y' TO WS-EOF.
       2000-ONE-ACCOUNT.
           IF AC-ST = 'A' AND AC-TY NOT = '40'
              PERFORM 2100-IDLE-DAYS
              IF WS-DAYS-IDLE > WS-LIMIT-DAYS
                 PERFORM 2200-LIVE-SO
                 IF WS-SO-FOUND = 'N'
                    PERFORM 2300-SWEEP
                 END-IF
              END-IF
           END-IF
           PERFORM 1000-READ-NEXT.
       2100-IDLE-DAYS.
      * AC-LTX IS YEAR AND DAY OF YEAR (YYYYDDD)
           COMPUTE WS-LTX-INT = FUNCTION INTEGER-OF-DAY (AC-LTX)
           COMPUTE WS-DAYS-IDLE = WS-TODAY-INT - WS-LTX-INT.
       2200-LIVE-SO.
           MOVE 'N' TO WS-SO-FOUND
           MOVE AC-NO TO SO-AC
           START SOMAST KEY NOT LESS THAN SO-AC
              INVALID KEY CONTINUE
              NOT INVALID KEY
                 READ SOMAST NEXT RECORD
                    AT END CONTINUE
                    NOT AT END
                       IF SO-AC = AC-NO AND SO-ST = 'A'
                          MOVE 'Y' TO WS-SO-FOUND
                       END-IF
                 END-READ
           END-START.
       2300-SWEEP.
           MOVE 'D' TO AC-ST
           REWRITE AC-REC
           MOVE AC-NO TO DM-AC
           MOVE WS-TODAY TO DM-DT
           MOVE 'S' TO DM-FG
           WRITE DM-REC
           PERFORM 2310-WRITE-LETTER
           ADD 1 TO WS-SWEPT.
"""

SORUN = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. SORUN.
      *---------------------------------------------------------------
      * STANDING ORDER RUN. EVERY MORNING BEFORE BRANCHES OPEN.
      * PAYS EVERY ACTIVE ORDER WHOSE NEXT DATE IS TODAY OR EARLIER.
      * IF THE PAYING ACCOUNT CANNOT COVER THE AMOUNT THE ORDER IS
      * SKIPPED AND LISTED ON THE EXCEPTION REPORT. IT IS NOT RETRIED.
      * THE NEXT DATE STILL MOVES ON.
      *---------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SOMAST ASSIGN TO SOMAST ORGANIZATION INDEXED
                  ACCESS MODE DYNAMIC RECORD KEY SO-ID
                  ALTERNATE RECORD KEY SO-ST-ND WITH DUPLICATES.
           SELECT ACMAST ASSIGN TO ACMAST ORGANIZATION INDEXED
                  ACCESS MODE RANDOM RECORD KEY AC-NO.
           SELECT EXCRPT ASSIGN TO EXCRPT.
       DATA DIVISION.
       FILE SECTION.
       FD  SOMAST.
       01  SO-REC.
           05 SO-ID        PIC X(8).
           05 SO-AC        PIC X(10).
           05 SO-BEN       PIC X(10).
           05 SO-AM        PIC S9(13) COMP-3.
           05 SO-FQ        PIC X.
           05 SO-ST-ND.
              10 SO-ST     PIC X.
              10 SO-ND     PIC 9(8).
       WORKING-STORAGE SECTION.
       01  WS-TODAY        PIC 9(8).
       01  WS-EOF          PIC X VALUE 'N'.
       01  WS-PAID         PIC 9(7) VALUE 0.
       01  WS-SKIPPED      PIC 9(7) VALUE 0.
       01  WS-ORIG-DAY     PIC 99.
       01  WS-NEXT         PIC 9(8).
       01  WS-NEXT-INT     PIC 9(7).
       PROCEDURE DIVISION.
       0000-MAIN.
           ACCEPT WS-TODAY FROM DATE YYYYMMDD
           OPEN I-O SOMAST
           OPEN I-O ACMAST
           OPEN OUTPUT EXCRPT
           MOVE 'A' TO SO-ST
           MOVE 0 TO SO-ND
           START SOMAST KEY NOT LESS THAN SO-ST-ND
              INVALID KEY MOVE 'Y' TO WS-EOF
           END-START
           PERFORM 2000-NEXT-ORDER UNTIL WS-EOF = 'Y'
           CLOSE SOMAST ACMAST EXCRPT
           DISPLAY 'SORUN PAID ' WS-PAID ' SKIPPED ' WS-SKIPPED
           STOP RUN.
       2000-NEXT-ORDER.
           READ SOMAST NEXT RECORD AT END MOVE 'Y' TO WS-EOF
           END-READ
           IF WS-EOF = 'N'
              IF SO-ST NOT = 'A' OR SO-ND > WS-TODAY
                 MOVE 'Y' TO WS-EOF
              ELSE
                 PERFORM 2100-TRY-TO-PAY
                 PERFORM 2200-MOVE-NEXT-DATE
                 REWRITE SO-REC
              END-IF
           END-IF.
       2100-TRY-TO-PAY.
           MOVE SO-AC TO AC-NO
           READ ACMAST
           IF AC-ST NOT = 'A' OR AC-BAL < SO-AM
      * AN OVERDRAWN ACCOUNT WITH AC-FLG1 = 'Y' MAY GO FURTHER OVERDRAWN
              IF AC-FLG1 = 'Y' AND AC-ST = 'A'
                 PERFORM 2110-PAY
              ELSE
                 WRITE EXC-LINE FROM SO-ID
                 ADD 1 TO WS-SKIPPED
              END-IF
           ELSE
              PERFORM 2110-PAY
           END-IF.
       2110-PAY.
           CALL 'POSTTXN' USING SO-AC '401' SO-AM 'D' SO-ID
           CALL 'POSTTXN' USING SO-BEN '402' SO-AM 'C' SO-ID
           ADD 1 TO WS-PAID.
       2200-MOVE-NEXT-DATE.
      * W = 7 DAYS. M = ONE MONTH. Q = THREE MONTHS.
      * IF THE DAY DOES NOT EXIST IN THE NEW MONTH USE THE LAST DAY.
      * THE ORIGINAL DAY IS KEPT IN SO-ND(7:2) ONLY WHILE IT FITS,
      * SO A 31ST ORDER GOES 31 JAN, 28 FEB, 28 MAR. THIS IS KNOWN.
           MOVE SO-ND (7:2) TO WS-ORIG-DAY
           EVALUATE SO-FQ
              WHEN 'W'
                 COMPUTE WS-NEXT-INT = FUNCTION INTEGER-OF-DATE (SO-ND) + 7
                 COMPUTE WS-NEXT = FUNCTION DATE-OF-INTEGER (WS-NEXT-INT)
              WHEN 'M'
                 PERFORM 2210-ADD-MONTHS-1
              WHEN 'Q'
                 PERFORM 2220-ADD-MONTHS-3
           END-EVALUATE
           MOVE WS-NEXT TO SO-ND.
"""

PROGRAMS = {
    "INTACCR": {"schedule": "nightly, after end of day", "source": INTACCR, "last_changed_days_ago": 1160},
    "STMTEXT": {"schedule": "monthly, second working day", "source": STMTEXT, "last_changed_days_ago": 720},
    "DORMSWP": {"schedule": "monthly, first day", "source": DORMSWP, "last_changed_days_ago": 540},
    "SORUN": {"schedule": "daily, before branches open", "source": SORUN, "last_changed_days_ago": 300},
}


def build_legacy(today: date) -> dict:
    procs = {}
    for name, p in PROCEDURES.items():
        procs[name] = {"procedure_name": name, "parameters": [{"name": a, "type": b} for a, b in p["parameters"]], "language": "SQL procedure",
                       "line_count": len(p["source"].splitlines()), "last_changed": d_ago(today, p["last_changed_days_ago"]), "source": p["source"],
                       "documentation_drafts": []}
    progs = {}
    for name, p in PROGRAMS.items():
        progs[name] = {"program_name": name, "language": "COBOL-style business language", "schedule": p["schedule"],
                       "line_count": len(p["source"].splitlines()), "last_changed": d_ago(today, p["last_changed_days_ago"]), "source": p["source"],
                       "documentation_drafts": [], "conversions": []}
    tables = build_tables(today)
    for t in tables.values():
        t["documentation_drafts"] = []
    return {"legacy_tables": tables, "legacy_procedures": procs, "legacy_programs": progs}
