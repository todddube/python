# Databricks notebook source
import re
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt

# COMMAND ----------

# MAGIC %md
# MAGIC ### Event: Reservation Created
# MAGIC 
# MAGIC **If we are limited to the consumption of MDM interaction events, this would be my preference for a the first one:**  
# MAGIC - Net new signal. Models already see most MDM interaction events (albeit on a delayed basis) through the batch Reltio FS. Reservations are not included in that list currently
# MAGIC - High volume without requiring additional integrations
# MAGIC   - Appraisal Created and Order Created are also high-volume MDM interaction events, but will require additional enrichment for vehicle details, etc.
# MAGIC 
# MAGIC [https://messaging.sites.carmax.com/event-types/b9ce7c3d-b870-451f-85e6-a8cf11f1aeae](https://messaging.sites.carmax.com/event-types/b9ce7c3d-b870-451f-85e6-a8cf11f1aeae)
# MAGIC ```
# MAGIC {
# MAGIC   "specversion": "1.0",
# MAGIC   "type": "com.carmax.customer.interaction.reservation.created.v1",
# MAGIC   "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1939507396450",
# MAGIC   "id": "8177ebf6-b07e-4a65-a889-cd6fc399560c",
# MAGIC   "time": "2020-11-27T14:33:02.3397332Z",
# MAGIC   "subject": "interactions/Reltio+1939507396450",
# MAGIC   "data": {
# MAGIC     "interactionId": "4085623177069",
# MAGIC     "sourceDateTimeUtc": "2020-11-30T19:55:30+00:00",
# MAGIC     "reservationId": "a38a99c1-9680-4bce-aec1-91974fff84a7",
# MAGIC     "stockNumber": "19523966",
# MAGIC     "identity": [
# MAGIC       {
# MAGIC         "type": "buysCustomerId",
# MAGIC         "value": "fe881c9f-db20-419c-9b81-580669830de2"
# MAGIC       },
# MAGIC       {
# MAGIC         "type": "crmId",
# MAGIC         "value": "0011C00002v2RwKQAU"
# MAGIC       },
# MAGIC       {
# MAGIC         "type": "storeCustomerId",
# MAGIC         "value": "155618",
# MAGIC         "meta": {
# MAGIC           "key": "locationId",
# MAGIC           "value": "7211"
# MAGIC         }
# MAGIC       }
# MAGIC     ]
# MAGIC   }
# MAGIC }
# MAGIC ```

# COMMAND ----------

sample_string = '''
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773891985235",
  "subject": "3773891985235",
  "time": "2021-10-07T14:53:57.9248488Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773891985235",
    "sourceDateTimeUtc": "2021-10-07T14:53:44+00:00",
    "stockNumber": "21069625",
    "reservationId": "cfae1c82-6b34-433e-b066-73fc7fef2c3f",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C0000336tmBQAQ"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~9TFgpbt"
      },
      {
        "type": "buysCustomerId",
        "value": "35dfaa3b-e575-40eb-b58d-ca91ef97a3dd"
      },
      {
        "type": "cafCustomerId",
        "value": "0014118320"
      },
      {
        "type": "storeCustomerId",
        "value": "660511",
        "meta": {
          "key": "locationId",
          "value": "7101"
        }
      },
      {
        "type": "ciamId",
        "value": "A92E07E6-3C68-41B5-B49D-BD0E792C927B"
      }
    ]
  },
  "id": "0591c6b1-cbb3-4513-a43d-185918a68b8b"
}
October 7, 2021 10:53 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812553387841",
  "subject": "812553387841",
  "time": "2021-10-07T14:53:18.7075935Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812553387841",
    "sourceDateTimeUtc": "2021-10-07T14:53:10+00:00",
    "stockNumber": "20822505",
    "reservationId": "c32b7608-fd8e-434c-989c-79c06d44e62c",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "80771",
        "meta": {
          "key": "locationId",
          "value": "7258"
        }
      },
      {
        "type": "ciamId",
        "value": "1C16D01F-40BE-4108-B918-C04C43BC7AA0"
      }
    ]
  },
  "id": "2941aaec-1696-455a-8868-5edcadfd8131"
}
October 7, 2021 10:52 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516414922559",
  "subject": "2516414922559",
  "time": "2021-10-07T14:52:50.6822301Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516414922559",
    "sourceDateTimeUtc": "2021-10-07T14:52:45+00:00",
    "stockNumber": "21055309",
    "reservationId": "d5b4448f-7934-4585-b663-d0d11e982bf9",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R0000360ZlwQAE"
      },
      {
        "type": "buysCustomerId",
        "value": "aea2b914-2eb8-45dd-ae49-efb2c277e656"
      },
      {
        "type": "ciamId",
        "value": "2399FDE1-CDAA-4A81-9B2D-A5A300F2F31E"
      },
      {
        "type": "storeCustomerId",
        "value": "711778",
        "meta": {
          "key": "locationId",
          "value": "7152"
        }
      }
    ]
  },
  "id": "d85bcb21-c86e-46f8-b88c-04386524e139"
}
October 7, 2021 10:51 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748148059971",
  "subject": "1748148059971",
  "time": "2021-10-07T14:51:58.8175382Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748148059971",
    "sourceDateTimeUtc": "2021-10-07T14:51:49+00:00",
    "stockNumber": "21415675",
    "reservationId": "e4c9be3a-2d9e-4105-b596-86e2598e7607",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002nXHLgQAO"
      },
      {
        "type": "storeCustomerId",
        "value": "732256",
        "meta": {
          "key": "locationId",
          "value": "7112"
        }
      },
      {
        "type": "ciamId",
        "value": "85936FBE-8A10-4CA5-8CCF-ED6F580116AF"
      },
      {
        "type": "buysCustomerId",
        "value": "44a4fd20-b950-4fb5-a8d7-d935703579e5"
      }
    ]
  },
  "id": "f1a0f23f-e801-477d-bef4-18cd2c4004b4"
}
October 7, 2021 10:51 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773889904467",
  "subject": "3773889904467",
  "time": "2021-10-07T14:51:16.6128357Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773889904467",
    "sourceDateTimeUtc": "2021-10-07T14:51:08+00:00",
    "stockNumber": "20780611",
    "reservationId": "5e2bb575-396d-46ac-bc84-6857964d841b",
    "identity": [
      {
        "type": "ciamId",
        "value": "12A60401-0EFE-4661-94AB-FEC6A8CDB2F6"
      },
      {
        "type": "storeCustomerId",
        "value": "162105",
        "meta": {
          "key": "locationId",
          "value": "6002"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~Qlymn3i"
      },
      {
        "type": "buysCustomerId",
        "value": "6674d5c8-f6d2-413a-a617-a04128d739b5"
      },
      {
        "type": "cafCustomerId",
        "value": "0014147921"
      },
      {
        "type": "crmId",
        "value": "0011C00002NQ0wvQAD"
      }
    ]
  },
  "id": "1a26529e-a027-47f3-bc98-df2276bd2dd9"
}
October 7, 2021 10:50 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988558466875",
  "subject": "2988558466875",
  "time": "2021-10-07T14:50:46.8698344Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988558466875",
    "sourceDateTimeUtc": "2021-10-07T14:50:36+00:00",
    "stockNumber": "21003812",
    "reservationId": "16854bdd-ee12-464c-b400-ece5d5a274b5",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000034o6LjQAI"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~ZIFFwJK"
      },
      {
        "type": "ciamId",
        "value": "A028D9A4-9AD8-4529-AEEC-AD6500CFF2A3"
      },
      {
        "type": "storeCustomerId",
        "value": "113152",
        "meta": {
          "key": "locationId",
          "value": "6031"
        }
      },
      {
        "type": "cafCustomerId",
        "value": "0014219643"
      },
      {
        "type": "buysCustomerId",
        "value": "853e5d16-d61e-44be-ad47-7cc02d56734e"
      }
    ]
  },
  "id": "46f55b16-2d94-4c84-bd55-4058c366d22e"
}
October 7, 2021 10:50 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352417439560",
  "subject": "2352417439560",
  "time": "2021-10-07T14:50:12.088296Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352417439560",
    "sourceDateTimeUtc": "2021-10-07T14:50:06+00:00",
    "stockNumber": "20891136",
    "reservationId": "0ae65228-fed5-457c-9c19-9dca5afbc4a6",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "155378",
        "meta": {
          "key": "locationId",
          "value": "7179"
        }
      },
      {
        "type": "ciamId",
        "value": "89B84B74-6C17-4FE5-937E-FD58F31C04EE"
      }
    ]
  },
  "id": "60b07a15-6b31-4606-a115-313c518906f9"
}
October 7, 2021 10:49 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352416784200",
  "subject": "2352416784200",
  "time": "2021-10-07T14:49:41.6468441Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352416784200",
    "sourceDateTimeUtc": "2021-10-07T14:49:31+00:00",
    "stockNumber": "21161065",
    "reservationId": "b037f6fb-1cb1-42d1-afb3-3a80fbf5a870",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036MBuaQAG"
      },
      {
        "type": "ciamId",
        "value": "2E4B0C68-242A-4F6C-B295-5B24D25466C1"
      },
      {
        "type": "buysCustomerId",
        "value": "3ecfa0a4-352f-4a9e-b333-01dd4a6fe678"
      },
      {
        "type": "storeCustomerId",
        "value": "396066",
        "meta": {
          "key": "locationId",
          "value": "7218"
        }
      }
    ]
  },
  "id": "78cd72ec-9f94-45e7-b82c-e213b18a6306"
}
October 7, 2021 10:49 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390504775503",
  "subject": "4390504775503",
  "time": "2021-10-07T14:49:03.3376755Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390504775503",
    "sourceDateTimeUtc": "2021-10-07T14:48:48+00:00",
    "stockNumber": "20926894",
    "reservationId": "e42a71aa-783b-40fa-94ac-052bde5e9fa0",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036OcieQAC"
      },
      {
        "type": "ciamId",
        "value": "77804DD1-FCF5-4812-8E5B-10A9031963FA"
      }
    ]
  },
  "id": "558a88c2-7506-4442-bcb1-8641a3842826"
}
October 7, 2021 10:48 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593956794166",
  "subject": "1593956794166",
  "time": "2021-10-07T14:48:11.8230359Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593956794166",
    "sourceDateTimeUtc": "2021-10-07T14:48:07+00:00",
    "stockNumber": "21332590",
    "reservationId": "d95eb1a5-f874-406b-a615-5c844a954bc7",
    "identity": [
      {
        "type": "ciamId",
        "value": "39CD7F1B-65E7-4BB1-AF2B-161E6F7B4A2B"
      },
      {
        "type": "storeCustomerId",
        "value": "711777",
        "meta": {
          "key": "locationId",
          "value": "7152"
        }
      }
    ]
  },
  "id": "f7c38b80-a835-498a-88f1-09f8fd00350e"
}
October 7, 2021 10:48 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988556713787",
  "subject": "2988556713787",
  "time": "2021-10-07T14:48:04.399641Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988556713787",
    "sourceDateTimeUtc": "2021-10-07T14:47:54+00:00",
    "stockNumber": "20919771",
    "reservationId": "ba6cb736-179c-4d2a-82b5-fc4460bc293d",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00001CGjVRQA1"
      },
      {
        "type": "ciamId",
        "value": "398EC4C2-0A09-4B85-891A-C65DB8AD7210"
      },
      {
        "type": "storeCustomerId",
        "value": "130935",
        "meta": {
          "key": "locationId",
          "value": "7231"
        }
      }
    ]
  },
  "id": "b3028053-7347-4670-af35-1bcdd3fec222"
}
October 7, 2021 10:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390503595855",
  "subject": "4390503595855",
  "time": "2021-10-07T14:47:34.8912104Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390503595855",
    "sourceDateTimeUtc": "2021-10-07T14:47:29+00:00",
    "stockNumber": "20826941",
    "reservationId": "1fa411b3-44cd-4acb-a1d2-13595576c236",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R00003624CvQAI"
      },
      {
        "type": "storeCustomerId",
        "value": "54340",
        "meta": {
          "key": "locationId",
          "value": "6049"
        }
      },
      {
        "type": "ciamId",
        "value": "C48070AD-662C-43BD-83D6-9B48CAB1F0D6"
      }
    ]
  },
  "id": "d323fae7-6134-4d78-8a66-912e3694858e"
}
October 7, 2021 10:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390503333711",
  "subject": "4390503333711",
  "time": "2021-10-07T14:47:18.9811287Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390503333711",
    "sourceDateTimeUtc": "2021-10-07T14:47:11+00:00",
    "stockNumber": "21021453",
    "reservationId": "f4f3c37c-ccb3-4e7c-88bc-636bc2483094",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C000026pqBjQAI"
      },
      {
        "type": "ciamId",
        "value": "B8824B39-752C-43AA-9A1C-0F33764C4F68"
      },
      {
        "type": "buysCustomerId",
        "value": "d73b2a8e-ee65-48bd-b452-940515564fa6"
      },
      {
        "type": "storeCustomerId",
        "value": "117218",
        "meta": {
          "key": "locationId",
          "value": "7270"
        }
      }
    ]
  },
  "id": "567cf7c9-c5cf-4045-bb06-fbab14133f82"
}
October 7, 2021 10:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812547948353",
  "subject": "812547948353",
  "time": "2021-10-07T14:46:01.2735269Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812547948353",
    "sourceDateTimeUtc": "2021-10-07T14:45:53+00:00",
    "stockNumber": "21319692",
    "reservationId": "7d2270a4-3573-47b4-bcc1-10dcaa386d5a",
    "identity": [
      {
        "type": "ciamId",
        "value": "A1C55444-D10E-4DF2-95C8-2D14F108D4FB"
      },
      {
        "type": "storeCustomerId",
        "value": "676073",
        "meta": {
          "key": "locationId",
          "value": "7101"
        }
      }
    ]
  },
  "id": "213e4e45-eead-4b11-8326-c6a52ecfd712"
}
October 7, 2021 10:45 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516409646911",
  "subject": "2516409646911",
  "time": "2021-10-07T14:45:30.5216935Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516409646911",
    "sourceDateTimeUtc": "2021-10-07T14:45:24+00:00",
    "stockNumber": "21318879",
    "reservationId": "bcdead47-8ef4-4951-9595-24e393cc5c5c",
    "identity": [
      {
        "type": "ciamId",
        "value": "EFE27A3A-82BB-41AA-927C-D22DE3A6AFEA"
      },
      {
        "type": "buysCustomerId",
        "value": "8338c297-0069-445a-960e-f79a53188410"
      },
      {
        "type": "storeCustomerId",
        "value": "46752",
        "meta": {
          "key": "locationId",
          "value": "6041"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002wZiztQAC"
      }
    ]
  },
  "id": "1a4b80ca-c444-4c67-8677-ce14fc322890"
}
October 7, 2021 10:44 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988554207035",
  "subject": "2988554207035",
  "time": "2021-10-07T14:44:52.8415028Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988554207035",
    "sourceDateTimeUtc": "2021-10-07T14:44:47+00:00",
    "stockNumber": "21019222",
    "reservationId": "a07ae2da-e7a9-4742-9b80-a52e01e0b3f9",
    "identity": [
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~NmGSvFd"
      },
      {
        "type": "storeCustomerId",
        "value": "1272546",
        "meta": {
          "key": "locationId",
          "value": "7104"
        }
      },
      {
        "type": "cafCustomerId",
        "value": "0013908894"
      },
      {
        "type": "ciamId",
        "value": "B2D56F42-8706-467A-AE34-9FF400F3FE2B"
      },
      {
        "type": "buysCustomerId",
        "value": "ecb9f243-1672-4341-91e8-4c55a3e7a6ba"
      },
      {
        "type": "crmId",
        "value": "0011C00002v0yR1QAI"
      }
    ]
  },
  "id": "a7908f54-397a-470f-a612-784e3d5dac94"
}
October 7, 2021 10:44 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812546604865",
  "subject": "812546604865",
  "time": "2021-10-07T14:44:49.7248544Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812546604865",
    "sourceDateTimeUtc": "2021-10-07T14:44:41+00:00",
    "stockNumber": "21214462",
    "reservationId": "b4a9457c-79a7-4d9d-a952-1166ceb06dc5",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "201266",
        "meta": {
          "key": "locationId",
          "value": "7257"
        }
      },
      {
        "type": "ciamId",
        "value": "AEA5100F-EC36-474D-A523-768F82791CEA"
      }
    ]
  },
  "id": "f401c73e-0483-4cd2-85fa-fae47d0c1df4"
}
October 7, 2021 10:44 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773885415251",
  "subject": "3773885415251",
  "time": "2021-10-07T14:44:49.7260681Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773885415251",
    "sourceDateTimeUtc": "2021-10-07T14:44:45+00:00",
    "stockNumber": "20876449",
    "reservationId": "f5b8da40-ef99-401f-8d16-7f285f4b89c8",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "5368366c-4998-4de1-ab02-4fbe05fc3838"
      },
      {
        "type": "crmId",
        "value": "0016R000034LP9iQAG"
      },
      {
        "type": "storeCustomerId",
        "value": "29315",
        "meta": {
          "key": "locationId",
          "value": "6112"
        }
      },
      {
        "type": "ciamId",
        "value": "D893E408-D82E-4C15-B5D0-ECACFF164937"
      }
    ]
  },
  "id": "9e26983c-2e5d-463d-a2fe-608120741799"
}
October 7, 2021 10:44 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748143161155",
  "subject": "1748143161155",
  "time": "2021-10-07T14:44:33.9648753Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748143161155",
    "sourceDateTimeUtc": "2021-10-07T14:44:30+00:00",
    "stockNumber": "20731436",
    "reservationId": "51046ba2-9e4a-4ba0-bae2-812457b51fcc",
    "identity": [
      {
        "type": "ciamId",
        "value": "97EEA89E-52F9-4F76-92B2-60657CD0B5C5"
      }
    ]
  },
  "id": "8c387686-3600-44f3-a90a-902b8c09c033"
}
October 7, 2021 10:43 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593953386294",
  "subject": "1593953386294",
  "time": "2021-10-07T14:43:53.7737386Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593953386294",
    "sourceDateTimeUtc": "2021-10-07T14:43:49+00:00",
    "stockNumber": "21162752",
    "reservationId": "8b873e32-25b6-4365-af20-1ce077f84b9e",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036ObjqQAC"
      },
      {
        "type": "ciamId",
        "value": "41DF9B44-6617-4E0A-9B78-978E542B8CA6"
      },
      {
        "type": "storeCustomerId",
        "value": "105333",
        "meta": {
          "key": "locationId",
          "value": "7285"
        }
      }
    ]
  },
  "id": "022f50cb-5aa2-4487-91d6-62a284629434"
}
October 7, 2021 10:43 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812545408833",
  "subject": "812545408833",
  "time": "2021-10-07T14:43:16.8596683Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812545408833",
    "sourceDateTimeUtc": "2021-10-07T14:43:09+00:00",
    "stockNumber": "20992684",
    "reservationId": "055b531d-aeaa-4f53-8e5e-8ddfa00bf655",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "ad0fda46-0286-4eb2-a650-8c0b35636355"
      },
      {
        "type": "storeCustomerId",
        "value": "333226",
        "meta": {
          "key": "locationId",
          "value": "7243"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00001ygtxlQAA"
      },
      {
        "type": "ciamId",
        "value": "4839FB66-90EA-4682-AFC5-320AD0A6162C"
      }
    ]
  },
  "id": "02f44513-1dd6-44d1-a23f-9c4a1bc24455"
}
October 7, 2021 10:42 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390500220751",
  "subject": "4390500220751",
  "time": "2021-10-07T14:42:51.6822712Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390500220751",
    "sourceDateTimeUtc": "2021-10-07T14:42:39+00:00",
    "stockNumber": "20803466",
    "reservationId": "5b861af3-9d1c-419e-8836-56ea40ba3bc8",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "223486",
        "meta": {
          "key": "locationId",
          "value": "7274"
        }
      },
      {
        "type": "ciamId",
        "value": "55D7A9F4-B088-4908-9E36-957B9A1D0171"
      }
    ]
  },
  "id": "77a552c4-00e0-4f2f-96d7-6a39d7d385ed"
}
October 7, 2021 10:42 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988552486715",
  "subject": "2988552486715",
  "time": "2021-10-07T14:42:19.5612442Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988552486715",
    "sourceDateTimeUtc": "2021-10-07T14:42:12+00:00",
    "stockNumber": "21206619",
    "reservationId": "59238e2f-cb76-4d24-9de2-14647cfa792d",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "1027067",
        "meta": {
          "key": "locationId",
          "value": "7132"
        }
      },
      {
        "type": "ciamId",
        "value": "55ACEB20-FC16-4F6A-8C1E-DFA83CC07165"
      },
      {
        "type": "buysCustomerId",
        "value": "a7f605ad-85c8-41c9-926a-b49d5e4980eb"
      },
      {
        "type": "crmId",
        "value": "0016R000036MzI7QAK"
      }
    ]
  },
  "id": "34bcecd1-d0a2-4782-8b11-ab5005d1cd05"
}
October 7, 2021 10:42 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593952288566",
  "subject": "1593952288566",
  "time": "2021-10-07T14:42:15.8147326Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593952288566",
    "sourceDateTimeUtc": "2021-10-07T14:42:06+00:00",
    "stockNumber": "20939326",
    "reservationId": "40e31d1a-25d8-4077-9fb0-65b4933059af",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "123191",
        "meta": {
          "key": "locationId",
          "value": "6031"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~KyMlbdF"
      },
      {
        "type": "buysCustomerId",
        "value": "72877849-8436-471a-a37f-f6e72e6f96cd"
      },
      {
        "type": "cafCustomerId",
        "value": "0013551660"
      },
      {
        "type": "ciamId",
        "value": "2428CE78-6B0E-4FC3-BA61-92F19B2468E4"
      },
      {
        "type": "crmId",
        "value": "0011C00002mEXotQAG"
      }
    ]
  },
  "id": "7adb5e6b-0bc7-41c8-a9a5-b972555c6627"
}
October 7, 2021 10:41 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390499352399",
  "subject": "4390499352399",
  "time": "2021-10-07T14:41:33.792369Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390499352399",
    "sourceDateTimeUtc": "2021-10-07T14:41:22+00:00",
    "stockNumber": "21170267",
    "reservationId": "b0dfb54f-cc5b-496f-b5f5-3afe13890358",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "50918",
        "meta": {
          "key": "locationId",
          "value": "7193"
        }
      },
      {
        "type": "ciamId",
        "value": "DB44178B-5A2D-4D94-9EA7-B4687B02C707"
      }
    ]
  },
  "id": "e5246df7-f190-49e0-b54e-53397cc76e74"
}
October 7, 2021 10:41 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096685563706",
  "subject": "2096685563706",
  "time": "2021-10-07T14:41:30.0844948Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096685563706",
    "sourceDateTimeUtc": "2021-10-07T14:41:24+00:00",
    "stockNumber": "21068015",
    "reservationId": "d9c41f95-7324-4a89-af9f-198eef70028e",
    "identity": [
      {
        "type": "ciamId",
        "value": "ACBC235F-D9A4-41CF-91A1-92B022864F77"
      },
      {
        "type": "buysCustomerId",
        "value": "77f570d5-7399-4b97-af82-65b3597500d6"
      },
      {
        "type": "crmId",
        "value": "0016R000036NbUQQA0"
      },
      {
        "type": "storeCustomerId",
        "value": "400560",
        "meta": {
          "key": "locationId",
          "value": "7185"
        }
      }
    ]
  },
  "id": "61472291-14e6-47fb-a9af-870e1a78ab7a"
}
October 7, 2021 10:40 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988551470907",
  "subject": "2988551470907",
  "time": "2021-10-07T14:40:52.508606Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988551470907",
    "sourceDateTimeUtc": "2021-10-07T14:40:42+00:00",
    "stockNumber": "21181050",
    "reservationId": "b361e285-0a87-40b4-b343-3c980c3dc388",
    "identity": [
      {
        "type": "ciamId",
        "value": "CE1F3B12-731D-4FD1-BE81-9136BD81D24F"
      },
      {
        "type": "cafCustomerId",
        "value": "0013311671"
      },
      {
        "type": "crmId",
        "value": "0011C00001zzNw5QAE"
      },
      {
        "type": "storeCustomerId",
        "value": "676070",
        "meta": {
          "key": "locationId",
          "value": "7101"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~fshcsun"
      },
      {
        "type": "buysCustomerId",
        "value": "92a920b9-d042-407d-811c-ccc16143d5d0"
      }
    ]
  },
  "id": "aa6d3f58-6e9a-4bcf-959c-bdd755ea4279"
}
October 7, 2021 10:39 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593949126454",
  "subject": "1593949126454",
  "time": "2021-10-07T14:39:31.1455438Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593949126454",
    "sourceDateTimeUtc": "2021-10-07T14:39:25+00:00",
    "stockNumber": "20558284",
    "reservationId": "16235446-0ee8-4716-87aa-9c06ce5f0acf",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036O7wqQAC"
      },
      {
        "type": "ciamId",
        "value": "E8953856-B53F-444C-B2D7-C80BD6B12480"
      },
      {
        "type": "storeCustomerId",
        "value": "134716",
        "meta": {
          "key": "locationId",
          "value": "6021"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "7aa28cf1-1d20-46d8-be30-be3285c7b279"
      }
    ]
  },
  "id": "a2ba275a-98f3-4249-b7e5-0e95d5ca9035"
}
October 7, 2021 10:39 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390495928143",
  "subject": "4390495928143",
  "time": "2021-10-07T14:39:12.9320032Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390495928143",
    "sourceDateTimeUtc": "2021-10-07T14:39:01+00:00",
    "stockNumber": "21260739",
    "reservationId": "52be2328-1f17-48f3-84b2-20322afd0e55",
    "identity": [
      {
        "type": "ciamId",
        "value": "F15D8E09-7402-4DF4-855A-C0BECF3C6820"
      },
      {
        "type": "storeCustomerId",
        "value": "667825",
        "meta": {
          "key": "locationId",
          "value": "7117"
        }
      }
    ]
  },
  "id": "ad657607-5bbd-442b-a02b-2654fae976f2"
}
October 7, 2021 10:37 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748137688899",
  "subject": "1748137688899",
  "time": "2021-10-07T14:37:46.4753639Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748137688899",
    "sourceDateTimeUtc": "2021-10-07T14:37:36+00:00",
    "stockNumber": "21058662",
    "reservationId": "b67c2bd9-a6cb-4ec5-950e-e67df8097961",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00001yfCu1QAE"
      },
      {
        "type": "storeCustomerId",
        "value": "577526",
        "meta": {
          "key": "locationId",
          "value": "7122"
        }
      },
      {
        "type": "cafCustomerId",
        "value": "0013531224"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~mIwonOo"
      },
      {
        "type": "ciamId",
        "value": "42723111-E587-4B60-897B-945F8570334E"
      }
    ]
  },
  "id": "b74cc8cf-3f6a-42a6-b96b-8938733a2b4d"
}
October 7, 2021 10:37 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352407068488",
  "subject": "2352407068488",
  "time": "2021-10-07T14:37:00.2777549Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352407068488",
    "sourceDateTimeUtc": "2021-10-07T14:36:50+00:00",
    "stockNumber": "21233467",
    "reservationId": "668546ee-9ee8-4e7e-a78a-4f7e4c0e5be7",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036ObrkQAC"
      },
      {
        "type": "ciamId",
        "value": "0DEB1A98-A136-4F21-BB76-30B57A818452"
      },
      {
        "type": "storeCustomerId",
        "value": "393909",
        "meta": {
          "key": "locationId",
          "value": "7148"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "520e4963-d25a-4b6c-870a-208073cd911e"
      }
    ]
  },
  "id": "e94cb2dd-4234-48a5-af82-a2d3ad543dda"
}
October 7, 2021 10:36 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352407035720",
  "subject": "2352407035720",
  "time": "2021-10-07T14:36:57.3711333Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352407035720",
    "sourceDateTimeUtc": "2021-10-07T14:36:43+00:00",
    "stockNumber": "21252417",
    "reservationId": "596276b5-8f90-4400-8efd-8f85f64b8384",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "116861",
        "meta": {
          "key": "locationId",
          "value": "7280"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036OPyWQAW"
      },
      {
        "type": "ciamId",
        "value": "FC54D639-94FF-4297-BA45-D5B3B2634BC1"
      },
      {
        "type": "buysCustomerId",
        "value": "381907da-f7fa-485d-bb87-767656dc05a0"
      }
    ]
  },
  "id": "b0f50d46-6f41-4fc9-bbba-45a93acc423d"
}
October 7, 2021 10:36 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748136820547",
  "subject": "1748136820547",
  "time": "2021-10-07T14:36:13.1415871Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748136820547",
    "sourceDateTimeUtc": "2021-10-07T14:36:00+00:00",
    "stockNumber": "20003797",
    "reservationId": "34a955b9-01a5-4532-a6ba-dc77aabec6dd",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "628372",
        "meta": {
          "key": "locationId",
          "value": "7105"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "5e58e907-5d39-4e62-8566-cb6e7e2eb114"
      },
      {
        "type": "crmId",
        "value": "0016R000036NwfKQAS"
      },
      {
        "type": "ciamId",
        "value": "F1AB089B-467C-4260-873A-352684A544F3"
      }
    ]
  },
  "id": "16807834-05a9-4d44-90c8-4502b0350b19"
}
October 7, 2021 10:35 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593945947958",
  "subject": "1593945947958",
  "time": "2021-10-07T14:35:36.6840205Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593945947958",
    "sourceDateTimeUtc": "2021-10-07T14:35:23+00:00",
    "stockNumber": "20857075",
    "reservationId": "0bfb6098-6c44-415a-97bf-c2dc74086251",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002wZquoQAC"
      },
      {
        "type": "storeCustomerId",
        "value": "176514",
        "meta": {
          "key": "locationId",
          "value": "6048"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "b8c0d734-5af9-43b9-9fc6-b9ad691a80ab"
      },
      {
        "type": "ciamId",
        "value": "132FD491-1A97-4FBB-AF33-1D755765458A"
      }
    ]
  },
  "id": "3f9e947e-c65b-49b6-a044-94eadfa72b75"
}
October 7, 2021 10:35 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096679108410",
  "subject": "2096679108410",
  "time": "2021-10-07T14:35:26.3446522Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096679108410",
    "sourceDateTimeUtc": "2021-10-07T14:35:07+00:00",
    "stockNumber": "20746132",
    "reservationId": "dbe51298-71bb-4a1c-ae4d-eb5a11a77897",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "39998",
        "meta": {
          "key": "locationId",
          "value": "6128"
        }
      },
      {
        "type": "ciamId",
        "value": "2C60954A-C46F-46C0-808D-DB64852BA6EA"
      }
    ]
  },
  "id": "12125177-aa74-41cf-a773-94c4f2e65187"
}
October 7, 2021 10:32 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773870112595",
  "subject": "3773870112595",
  "time": "2021-10-07T14:32:17.3180785Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773870112595",
    "sourceDateTimeUtc": "2021-10-07T14:32:08+00:00",
    "stockNumber": "21118954",
    "reservationId": "d2fad645-108e-410e-9a64-8958e7aa4b5b",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000035A1WtQAK"
      },
      {
        "type": "buysCustomerId",
        "value": "0ef6207a-19cb-43f1-abcf-91267b3b54df"
      },
      {
        "type": "storeCustomerId",
        "value": "24842",
        "meta": {
          "key": "locationId",
          "value": "6140"
        }
      },
      {
        "type": "ciamId",
        "value": "1E1A38E2-D6EC-446B-AC63-077AE2ABED5A"
      }
    ]
  },
  "id": "7746e150-3c70-461e-8fc7-42ad85494cd6"
}
October 7, 2021 10:32 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812530941761",
  "subject": "812530941761",
  "time": "2021-10-07T14:32:01.2986627Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812530941761",
    "sourceDateTimeUtc": "2021-10-07T14:31:56+00:00",
    "stockNumber": "20969138",
    "reservationId": "a32d15e4-c5ca-4357-a873-7cb819a0b226",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "66622",
        "meta": {
          "key": "locationId",
          "value": "6082"
        }
      },
      {
        "type": "cafCustomerId",
        "value": "0012985193"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~JIG16Sl"
      },
      {
        "type": "crmId",
        "value": "0011C00002F25QMQAZ"
      },
      {
        "type": "ciamId",
        "value": "5D977D62-1037-4633-80D2-A3D50121CEEE"
      }
    ]
  },
  "id": "75fe3bc4-c6fd-4d9f-819a-f3a359ab5fe7"
}
October 7, 2021 10:29 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748122107715",
  "subject": "1748122107715",
  "time": "2021-10-07T14:29:56.6841185Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748122107715",
    "sourceDateTimeUtc": "2021-10-07T14:29:45+00:00",
    "stockNumber": "21042201",
    "reservationId": "8b32ccef-ac95-4b54-b406-cac383b6b84c",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002TJMX8QAP"
      },
      {
        "type": "storeCustomerId",
        "value": "122510",
        "meta": {
          "key": "locationId",
          "value": "7271"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~HL2ZwjG"
      },
      {
        "type": "ciamId",
        "value": "9085043A-6F0E-4702-B347-FA8DEDD2A4CE"
      },
      {
        "type": "buysCustomerId",
        "value": "32da387e-7de1-4aab-9775-acdb3c30b7f8"
      }
    ]
  },
  "id": "5525e6e2-8ff9-4a0b-8ab6-80c742c17edf"
}
October 7, 2021 10:29 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773862641491",
  "subject": "3773862641491",
  "time": "2021-10-07T14:29:12.7630938Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773862641491",
    "sourceDateTimeUtc": "2021-10-07T14:29:02+00:00",
    "stockNumber": "20515488",
    "reservationId": "7c99b319-ff93-4d08-ba06-2b53ed78e2f5",
    "identity": [
      {
        "type": "ciamId",
        "value": "86BA2808-5725-4773-A826-C64303FE8A75"
      },
      {
        "type": "storeCustomerId",
        "value": "78729",
        "meta": {
          "key": "locationId",
          "value": "6040"
        }
      }
    ]
  },
  "id": "49102dfc-8595-4698-97bf-271196ded536"
}
October 7, 2021 10:29 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593928957750",
  "subject": "1593928957750",
  "time": "2021-10-07T14:29:01.6286471Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593928957750",
    "sourceDateTimeUtc": "2021-10-07T14:28:57+00:00",
    "stockNumber": "20979910",
    "reservationId": "e59b41ad-fe30-4fac-80a3-1882bea12722",
    "identity": [
      {
        "type": "ciamId",
        "value": "0219EAC8-2143-41F7-8DB7-56F50179CD0B"
      },
      {
        "type": "storeCustomerId",
        "value": "76666",
        "meta": {
          "key": "locationId",
          "value": "6011"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002sTf0KQAS"
      }
    ]
  },
  "id": "ac647c66-734f-447b-a997-cb9777beb421"
}
October 7, 2021 10:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390477725519",
  "subject": "4390477725519",
  "time": "2021-10-07T14:28:50.5723461Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390477725519",
    "sourceDateTimeUtc": "2021-10-07T14:28:39+00:00",
    "stockNumber": "21013040",
    "reservationId": "0a5647f4-c454-4fdc-ae3e-2f4147ee0fd1",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002k9zneQAA"
      },
      {
        "type": "storeCustomerId",
        "value": "628713",
        "meta": {
          "key": "locationId",
          "value": "7105"
        }
      },
      {
        "type": "ciamId",
        "value": "37B3C222-087F-478E-A9C3-A43900C6986A"
      }
    ]
  },
  "id": "4ba46950-58c0-45b4-879c-e5749cf496bc"
}
October 7, 2021 10:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593927581494",
  "subject": "1593927581494",
  "time": "2021-10-07T14:28:29.5079843Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593927581494",
    "sourceDateTimeUtc": "2021-10-07T14:28:20+00:00",
    "stockNumber": "21247576",
    "reservationId": "22c44d83-4121-4ff9-a58e-0c8d232dca84",
    "identity": [
      {
        "type": "ciamId",
        "value": "AEEDD21A-9C41-4660-84D4-C1C467340405"
      },
      {
        "type": "storeCustomerId",
        "value": "552422",
        "meta": {
          "key": "locationId",
          "value": "7195"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~vquOBWf"
      },
      {
        "type": "crmId",
        "value": "0016R0000363OkXQAU"
      }
    ]
  },
  "id": "1711e78a-7126-44f9-be27-649622a1a7de"
}
October 7, 2021 10:27 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390475251535",
  "subject": "4390475251535",
  "time": "2021-10-07T14:27:57.2712608Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390475251535",
    "sourceDateTimeUtc": "2021-10-07T14:27:40+00:00",
    "stockNumber": "21009555",
    "reservationId": "88d8efd0-2080-4ce8-9bea-169b69e54bcc",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036OcNMQA0"
      },
      {
        "type": "ciamId",
        "value": "CB3196AF-39E1-422F-AE8B-A22700A9FB19"
      }
    ]
  },
  "id": "69059e36-f2c9-4eed-b2a0-66e03564abe3"
}
October 7, 2021 10:27 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593924878134",
  "subject": "1593924878134",
  "time": "2021-10-07T14:27:22.1760069Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593924878134",
    "sourceDateTimeUtc": "2021-10-07T14:27:15+00:00",
    "stockNumber": "20573304",
    "reservationId": "b785446e-58ac-4bfe-bcd4-9ec95a7c3847",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "295369",
        "meta": {
          "key": "locationId",
          "value": "7190"
        }
      },
      {
        "type": "ciamId",
        "value": "90211BCE-DDC4-4EAA-8155-441E7E50AF15"
      }
    ]
  },
  "id": "7948cc50-6643-4851-a0c5-8788a0819b47"
}
October 7, 2021 10:26 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812515835713",
  "subject": "812515835713",
  "time": "2021-10-07T14:26:25.7181397Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812515835713",
    "sourceDateTimeUtc": "2021-10-07T14:26:15+00:00",
    "stockNumber": "21189193",
    "reservationId": "e25bced4-1b54-4570-b8ac-2cdb1beb73cb",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "c6c3e1ec-6239-4adb-bdea-45ae77f03995"
      },
      {
        "type": "crmId",
        "value": "0016R000035c69vQAA"
      },
      {
        "type": "storeCustomerId",
        "value": "716883",
        "meta": {
          "key": "locationId",
          "value": "7128"
        }
      },
      {
        "type": "ciamId",
        "value": "E514696B-C0BA-476F-8856-8FC9E2504095"
      }
    ]
  },
  "id": "af11bf5c-fbbd-4079-b310-cf90ae0fcb9f"
}
October 7, 2021 10:26 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516376371007",
  "subject": "2516376371007",
  "time": "2021-10-07T14:26:17.5318977Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516376371007",
    "sourceDateTimeUtc": "2021-10-07T14:26:07+00:00",
    "stockNumber": "21212808",
    "reservationId": "5ea5ccfa-101d-4d29-99ba-886da0465678",
    "identity": [
      {
        "type": "ciamId",
        "value": "81F4BB01-8DA5-4C29-88D2-103A5BA152E4"
      }
    ]
  },
  "id": "e4950e65-a64b-4893-8b50-c3f3bc5b08e5"
}
October 7, 2021 10:25 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516374552383",
  "subject": "2516374552383",
  "time": "2021-10-07T14:25:29.7992077Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516374552383",
    "sourceDateTimeUtc": "2021-10-07T14:25:15+00:00",
    "stockNumber": "21361581",
    "reservationId": "00f55a29-faae-47ac-934d-a74bcd42b96a",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "123190",
        "meta": {
          "key": "locationId",
          "value": "6031"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~UG8jz07"
      },
      {
        "type": "buysCustomerId",
        "value": "bad38e8f-208f-4cb4-aff1-2af8c4a04019"
      },
      {
        "type": "crmId",
        "value": "0011C00002wYPbSQAW"
      },
      {
        "type": "ciamId",
        "value": "E29F492E-3A8D-40A3-9B8F-B94AF801071A"
      }
    ]
  },
  "id": "600be4d9-b0d3-468a-b4b4-067a1720bb6f"
}
October 7, 2021 10:24 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812512182081",
  "subject": "812512182081",
  "time": "2021-10-07T14:24:37.5576729Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812512182081",
    "sourceDateTimeUtc": "2021-10-07T14:24:28+00:00",
    "stockNumber": "19920058",
    "reservationId": "ffcc0b46-7962-4249-9ba8-342dfa1522f4",
    "identity": [
      {
        "type": "ciamId",
        "value": "96A8BA9D-E97A-4B40-B082-D78F4FD09557"
      }
    ]
  },
  "id": "db1192e2-f4fb-40af-b84d-d018e748c334"
}
October 7, 2021 10:24 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812511231809",
  "subject": "812511231809",
  "time": "2021-10-07T14:24:20.0046319Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812511231809",
    "sourceDateTimeUtc": "2021-10-07T14:24:07+00:00",
    "stockNumber": "21131703",
    "reservationId": "1ee506ad-49e8-4f18-ae22-1b1b3131e282",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "628711",
        "meta": {
          "key": "locationId",
          "value": "7105"
        }
      },
      {
        "type": "ciamId",
        "value": "BD76F0E0-3780-4D4C-BCC3-1C4424F8BF18"
      }
    ]
  },
  "id": "007b616a-365c-4813-9c43-9de91e78c634"
}
October 7, 2021 10:23 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593914507062",
  "subject": "1593914507062",
  "time": "2021-10-07T14:23:25.7707353Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593914507062",
    "sourceDateTimeUtc": "2021-10-07T14:23:14+00:00",
    "stockNumber": "21118634",
    "reservationId": "f7ae2126-5879-41da-ae0d-7c366194d9a2",
    "identity": [
      {
        "type": "ciamId",
        "value": "9F1B6FDE-9289-413B-8637-761AF3FF7759"
      },
      {
        "type": "storeCustomerId",
        "value": "711773",
        "meta": {
          "key": "locationId",
          "value": "7152"
        }
      }
    ]
  },
  "id": "5425556d-80ab-4300-a629-e324fc3e5fad"
}
October 7, 2021 10:21 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748100857667",
  "subject": "1748100857667",
  "time": "2021-10-07T14:21:44.7161317Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748100857667",
    "sourceDateTimeUtc": "2021-10-07T14:21:33+00:00",
    "stockNumber": "20960954",
    "reservationId": "126f0c59-062e-43ed-818e-1ee919df209f",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "1aadb44a-ae7e-4798-9d5b-d0d2e63b7376"
      },
      {
        "type": "storeCustomerId",
        "value": "252343",
        "meta": {
          "key": "locationId",
          "value": "7654"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~YF9WkAa"
      },
      {
        "type": "ciamId",
        "value": "9E874D14-763D-4BE5-87F0-75C3CD745D48"
      },
      {
        "type": "crmId",
        "value": "0016R000035ptZNQAY"
      }
    ]
  },
  "id": "81eb5f9c-edbf-4003-b4ab-01daea528c76"
}
October 7, 2021 10:20 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748097220419",
  "subject": "1748097220419",
  "time": "2021-10-07T14:20:17.6627584Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748097220419",
    "sourceDateTimeUtc": "2021-10-07T14:20:05+00:00",
    "stockNumber": "21129632",
    "reservationId": "28729cb2-3422-47fe-9aff-e97cf254b2e2",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036Oc8bQAC"
      },
      {
        "type": "buysCustomerId",
        "value": "0be0418f-34ad-4d0e-9edf-61b0fdd19c4a"
      },
      {
        "type": "storeCustomerId",
        "value": "526905",
        "meta": {
          "key": "locationId",
          "value": "7146"
        }
      },
      {
        "type": "ciamId",
        "value": "1114CDB3-AB48-475E-A14E-DA11A8855DEF"
      }
    ]
  },
  "id": "c64d5920-6ad0-473f-ad8c-94f48077b817"
}
October 7, 2021 10:19 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390453591887",
  "subject": "4390453591887",
  "time": "2021-10-07T14:19:40.148426Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390453591887",
    "sourceDateTimeUtc": "2021-10-07T14:19:32+00:00",
    "stockNumber": "20671935",
    "reservationId": "bac6f9c5-191f-4111-892b-2c1646682d85",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "32194",
        "meta": {
          "key": "locationId",
          "value": "6121"
        }
      },
      {
        "type": "ciamId",
        "value": "AF00CFD3-850B-459D-B9E3-62AB9D805F62"
      }
    ]
  },
  "id": "2c0e7f6b-4d97-4fae-8aa1-f792978daa11"
}
October 7, 2021 10:19 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352366452552",
  "subject": "2352366452552",
  "time": "2021-10-07T14:19:40.1469759Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352366452552",
    "sourceDateTimeUtc": "2021-10-07T14:19:31+00:00",
    "stockNumber": "21353053",
    "reservationId": "0f508eb7-d4dd-4e18-9d7a-0322188f5a29",
    "identity": [
      {
        "type": "ciamId",
        "value": "04CA6BAA-1D3E-4E4B-828C-C462CB22E2DE"
      },
      {
        "type": "buysCustomerId",
        "value": "f3655ebe-5c3c-409c-9472-508c7e89c18b"
      },
      {
        "type": "storeCustomerId",
        "value": "232346",
        "meta": {
          "key": "locationId",
          "value": "7291"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002ocpwhQAA"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~15TCsia4"
      }
    ]
  },
  "id": "6319c212-3908-47ea-a24f-561f39265d3b"
}
October 7, 2021 10:18 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096640212794",
  "subject": "2096640212794",
  "time": "2021-10-07T14:18:49.9927006Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096640212794",
    "sourceDateTimeUtc": "2021-10-07T14:18:38+00:00",
    "stockNumber": "21332746",
    "reservationId": "c5f2a231-74e9-496e-af40-33edd6e8c761",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000033sHQbQAM"
      },
      {
        "type": "buysCustomerId",
        "value": "729eeb5b-8870-4f8c-9009-7a2f289116b5"
      },
      {
        "type": "ciamId",
        "value": "4677F99E-B73C-40A1-9827-8FA9965F4253"
      },
      {
        "type": "storeCustomerId",
        "value": "711772",
        "meta": {
          "key": "locationId",
          "value": "7152"
        }
      }
    ]
  },
  "id": "8c25065e-7ad6-424a-904a-44eae6a97a3b"
}
October 7, 2021 10:16 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096634691386",
  "subject": "2096634691386",
  "time": "2021-10-07T14:16:49.913355Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096634691386",
    "sourceDateTimeUtc": "2021-10-07T14:16:33+00:00",
    "stockNumber": "20860315",
    "reservationId": "b49436de-6072-4bd9-bcde-09ed26ac4807",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "232344",
        "meta": {
          "key": "locationId",
          "value": "7291"
        }
      },
      {
        "type": "ciamId",
        "value": "EE339F81-7039-4DC0-A99A-8022BB0161CE"
      },
      {
        "type": "crmId",
        "value": "0011C00002cs9AyQAI"
      }
    ]
  },
  "id": "97f18b84-59a6-4ac4-b753-615fd0205fb4"
}
October 7, 2021 10:15 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748085833539",
  "subject": "1748085833539",
  "time": "2021-10-07T14:15:30.2693709Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748085833539",
    "sourceDateTimeUtc": "2021-10-07T14:15:25+00:00",
    "stockNumber": "21133325",
    "reservationId": "0b666dd5-f92d-4bb3-9a6b-67c414d4d36a",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "896840",
        "meta": {
          "key": "locationId",
          "value": "7102"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~vos9MTV"
      },
      {
        "type": "ciamId",
        "value": "2583E626-9BDA-4B72-BFB5-ED71F275CD7E"
      },
      {
        "type": "crmId",
        "value": "0016R00003631rkQAA"
      },
      {
        "type": "buysCustomerId",
        "value": "efc95c5b-4486-4a89-abd8-5c6f5c28988c"
      }
    ]
  },
  "id": "16f714e7-f83b-4b27-9149-6be63be57212"
}
October 7, 2021 10:15 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773827972947",
  "subject": "3773827972947",
  "time": "2021-10-07T14:15:30.0275546Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773827972947",
    "sourceDateTimeUtc": "2021-10-07T14:15:22+00:00",
    "stockNumber": "21121389",
    "reservationId": "66ae4e5b-64eb-4d0d-899c-f34401d4b9a4",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C000026sQbMQAU"
      },
      {
        "type": "storeCustomerId",
        "value": "323491",
        "meta": {
          "key": "locationId",
          "value": "7204"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~WYNbVjV"
      },
      {
        "type": "buysCustomerId",
        "value": "de1c5ef7-4678-4452-8f8f-69e0fd9b5118"
      },
      {
        "type": "ciamId",
        "value": "CF8EEB76-5CAC-49FB-95AE-47D25B9B58DE"
      }
    ]
  },
  "id": "efbf52bb-4b0e-4dea-ae4a-5df20215a4c6"
}
October 7, 2021 10:14 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390441221967",
  "subject": "4390441221967",
  "time": "2021-10-07T14:14:24.8073805Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390441221967",
    "sourceDateTimeUtc": "2021-10-07T14:14:17+00:00",
    "stockNumber": "20971408",
    "reservationId": "55660c69-bb29-43d0-b2a7-c99d6ff44a29",
    "identity": [
      {
        "type": "ciamId",
        "value": "7707CCEF-E2BB-4691-9352-208DAB0BC3D9"
      }
    ]
  },
  "id": "0fc4a987-b9c8-44b1-b0d8-b1de34941543"
}
October 7, 2021 10:14 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096629153594",
  "subject": "2096629153594",
  "time": "2021-10-07T14:14:16.5346211Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096629153594",
    "sourceDateTimeUtc": "2021-10-07T14:14:11+00:00",
    "stockNumber": "20567074",
    "reservationId": "e1e03dac-5157-4864-86be-7e34c10517b3",
    "identity": [
      {
        "type": "ciamId",
        "value": "8436AF5C-EDEB-4D3F-BD8E-90EFC5C837D7"
      }
    ]
  },
  "id": "7d799256-b1ff-46c6-b6aa-3000e5fd9322"
}
October 7, 2021 10:13 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988493848379",
  "subject": "2988493848379",
  "time": "2021-10-07T14:13:57.4521445Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988493848379",
    "sourceDateTimeUtc": "2021-10-07T14:13:49+00:00",
    "stockNumber": "21317209",
    "reservationId": "13503741-88c7-427e-9a72-b0fdf2f4786a",
    "identity": [
      {
        "type": "ciamId",
        "value": "B4F85B24-D623-49F0-BD96-5C3EC1E89664"
      }
    ]
  },
  "id": "b896a528-4633-4fad-9293-e84094404641"
}
October 7, 2021 10:12 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516342341439",
  "subject": "2516342341439",
  "time": "2021-10-07T14:12:26.5783835Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516342341439",
    "sourceDateTimeUtc": "2021-10-07T14:12:20+00:00",
    "stockNumber": "21089297",
    "reservationId": "2fe2ea5e-2214-4741-bc59-eb07f49f4aeb",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "344418",
        "meta": {
          "key": "locationId",
          "value": "7157"
        }
      },
      {
        "type": "ciamId",
        "value": "E5204DFE-F54B-4187-99AB-2AC835509FCF"
      },
      {
        "type": "crmId",
        "value": "0011C00002Fa9mUQAR"
      }
    ]
  },
  "id": "8f881fdb-1ea7-4f8c-b0ce-b1cf9e76a974"
}
October 7, 2021 10:12 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773820125011",
  "subject": "3773820125011",
  "time": "2021-10-07T14:12:02.8417508Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773820125011",
    "sourceDateTimeUtc": "2021-10-07T14:11:53+00:00",
    "stockNumber": "21188311",
    "reservationId": "9df5f203-eaae-4eb5-868b-f09181f9f384",
    "identity": [
      {
        "type": "ciamId",
        "value": "8A9B56A3-0380-4AE5-9D11-A06900AA112C"
      },
      {
        "type": "storeCustomerId",
        "value": "44841",
        "meta": {
          "key": "locationId",
          "value": "6020"
        }
      }
    ]
  },
  "id": "6d32ef24-9284-44ea-906b-17d41ef2fd32"
}
October 7, 2021 10:10 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390433767247",
  "subject": "4390433767247",
  "time": "2021-10-07T14:10:01.509394Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390433767247",
    "sourceDateTimeUtc": "2021-10-07T14:09:51+00:00",
    "stockNumber": "21297150",
    "reservationId": "13619b6a-6344-416b-908d-b1d59b86ea7a",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "52547",
        "meta": {
          "key": "locationId",
          "value": "6056"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036N3tlQAC"
      },
      {
        "type": "buysCustomerId",
        "value": "c347c774-9533-44d9-b9c2-0ca9c46888f1"
      },
      {
        "type": "ciamId",
        "value": "54D91674-1962-484A-B4B7-15A0B6EC8743"
      }
    ]
  },
  "id": "e463882d-52fc-4879-b79a-9312ea6c271e"
}
October 7, 2021 10:09 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773819125587",
  "subject": "3773819125587",
  "time": "2021-10-07T14:09:37.8982434Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773819125587",
    "sourceDateTimeUtc": "2021-10-07T14:09:27+00:00",
    "stockNumber": "21189836",
    "reservationId": "2e216b73-fbc6-4574-86a8-3ccf128d449d",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "fa821da0-cdee-4b12-b7e4-8846555d9bee"
      },
      {
        "type": "storeCustomerId",
        "value": "341627",
        "meta": {
          "key": "locationId",
          "value": "7208"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~L8erSSK"
      },
      {
        "type": "crmId",
        "value": "0016R000035Qr8KQAS"
      },
      {
        "type": "ciamId",
        "value": "FBB0506E-9A74-4CA0-A38D-40ACFB64CE84"
      }
    ]
  },
  "id": "06b3bd9a-9fd0-4edb-a20a-26d7f729f223"
}
October 7, 2021 10:09 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748076412739",
  "subject": "1748076412739",
  "time": "2021-10-07T14:09:21.7198399Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748076412739",
    "sourceDateTimeUtc": "2021-10-07T14:09:17+00:00",
    "stockNumber": "20738575",
    "reservationId": "bb32e848-1e12-42d6-a0ab-65a98352ec05",
    "identity": [
      {
        "type": "ciamId",
        "value": "DFB1CF09-C61A-43D0-B4BE-4ED20C5064A9"
      },
      {
        "type": "storeCustomerId",
        "value": "315845",
        "meta": {
          "key": "locationId",
          "value": "7663"
        }
      }
    ]
  },
  "id": "2b6065cd-1347-4c95-b060-0610aba3bbe9"
}
October 7, 2021 10:07 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593886326582",
  "subject": "1593886326582",
  "time": "2021-10-07T14:07:00.652657Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593886326582",
    "sourceDateTimeUtc": "2021-10-07T14:06:48+00:00",
    "stockNumber": "20591309",
    "reservationId": "0f7bec4e-d12d-4cd1-a3a5-6378349baf37",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "333221",
        "meta": {
          "key": "locationId",
          "value": "7243"
        }
      },
      {
        "type": "ciamId",
        "value": "4DE6FE36-5596-4895-ADD4-BC3F80556D8E"
      }
    ]
  },
  "id": "be33738d-a86d-4a92-8131-e72c9d75638c"
}
October 7, 2021 10:06 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773817306963",
  "subject": "3773817306963",
  "time": "2021-10-07T14:06:33.9149106Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773817306963",
    "sourceDateTimeUtc": "2021-10-07T14:06:20+00:00",
    "stockNumber": "21186641",
    "reservationId": "d41be912-1ee2-4c1c-a272-8e6ec6bd1b9c",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036MaEQQA0"
      },
      {
        "type": "storeCustomerId",
        "value": "1290685",
        "meta": {
          "key": "locationId",
          "value": "7104"
        }
      },
      {
        "type": "ciamId",
        "value": "3480141D-FB55-42A8-AA63-89A44D625AE5"
      },
      {
        "type": "buysCustomerId",
        "value": "3a59ea83-e600-4dd3-af5a-614326361518"
      }
    ]
  },
  "id": "92b2685d-2e49-4aa0-9697-69a05ac1d65f"
}
October 7, 2021 10:06 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812477366081",
  "subject": "812477366081",
  "time": "2021-10-07T14:06:13.0073864Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812477366081",
    "sourceDateTimeUtc": "2021-10-07T14:06:07+00:00",
    "stockNumber": "21133798",
    "reservationId": "1263d2d5-22ec-4084-baa6-33d4e6f176cd",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "228373",
        "meta": {
          "key": "locationId",
          "value": "7278"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002apyyCQAQ"
      },
      {
        "type": "buysCustomerId",
        "value": "3bd350de-adee-4f0c-924e-efb24e2f9b25"
      },
      {
        "type": "ciamId",
        "value": "59C7241C-01C2-42D4-82B6-096981291B00"
      },
      {
        "type": "cafCustomerId",
        "value": "0013768164"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~11n6ZszN"
      }
    ]
  },
  "id": "5d245667-4873-427e-a383-eac9f00bbfeb"
}
October 7, 2021 10:05 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593885163318",
  "subject": "1593885163318",
  "time": "2021-10-07T14:05:21.8291993Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593885163318",
    "sourceDateTimeUtc": "2021-10-07T14:05:17+00:00",
    "stockNumber": "21245299",
    "reservationId": "48de8c32-4b9b-45fd-9aa2-280fc62c202f",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002XtgNHQAZ"
      },
      {
        "type": "buysCustomerId",
        "value": "0454c368-1e4d-4ca9-ba12-5e9d1f2ae2a2"
      },
      {
        "type": "storeCustomerId",
        "value": "824240",
        "meta": {
          "key": "locationId",
          "value": "7114"
        }
      },
      {
        "type": "ciamId",
        "value": "92E2AB8F-882D-4E1B-8CD9-9AD5088AC48C"
      }
    ]
  },
  "id": "7249f480-7e8d-4fff-9e21-e855d8173235"
}
October 7, 2021 10:04 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390430359375",
  "subject": "4390430359375",
  "time": "2021-10-07T14:04:15.1716733Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390430359375",
    "sourceDateTimeUtc": "2021-10-07T14:04:05+00:00",
    "stockNumber": "21034133",
    "reservationId": "8014e40e-d3e2-45f4-907a-c9a0a8d97e90",
    "identity": [
      {
        "type": "ciamId",
        "value": "39967150-DBAB-42A0-9E83-2271107F494A"
      },
      {
        "type": "crmId",
        "value": "0011C000032MFITQA4"
      },
      {
        "type": "storeCustomerId",
        "value": "94841",
        "meta": {
          "key": "locationId",
          "value": "6063"
        }
      }
    ]
  },
  "id": "feabdc9e-0b0d-4c77-9ea0-4078bcf96cc0"
}
October 7, 2021 10:04 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096620076858",
  "subject": "2096620076858",
  "time": "2021-10-07T14:04:04.356575Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096620076858",
    "sourceDateTimeUtc": "2021-10-07T14:03:57+00:00",
    "stockNumber": "21306935",
    "reservationId": "0239687b-6dff-437d-b626-055a872b2f23",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "809312",
        "meta": {
          "key": "locationId",
          "value": "7106"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036MvRUQA0"
      },
      {
        "type": "buysCustomerId",
        "value": "8a187809-8530-4402-929d-8782507b6292"
      },
      {
        "type": "ciamId",
        "value": "6A0F38E0-1525-46EC-A7EF-3EED46E5F42A"
      }
    ]
  },
  "id": "354d69db-907a-4838-9ac8-1867f4067e5b"
}
October 7, 2021 10:03 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390429769551",
  "subject": "4390429769551",
  "time": "2021-10-07T14:03:04.52906Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390429769551",
    "sourceDateTimeUtc": "2021-10-07T14:02:56+00:00",
    "stockNumber": "21357250",
    "reservationId": "792549e6-4453-480d-9df9-7e8e0ce1784b",
    "identity": [
      {
        "type": "ciamId",
        "value": "3E1D35E5-2FAA-4C3B-8093-F9B2F36F43AE"
      },
      {
        "type": "storeCustomerId",
        "value": "266248",
        "meta": {
          "key": "locationId",
          "value": "7248"
        }
      }
    ]
  },
  "id": "30262894-19ad-4330-ac7c-b42f9c72d42b"
}
October 7, 2021 10:02 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516336475967",
  "subject": "2516336475967",
  "time": "2021-10-07T14:02:56.2890584Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516336475967",
    "sourceDateTimeUtc": "2021-10-07T14:02:47+00:00",
    "stockNumber": "21351996",
    "reservationId": "27152122-9fa4-4916-8357-bcf59e6dddba",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "274982",
        "meta": {
          "key": "locationId",
          "value": "7180"
        }
      },
      {
        "type": "ciamId",
        "value": "19094CF5-E55D-4838-A023-D1E0C002EC3B"
      },
      {
        "type": "crmId",
        "value": "0011C00002arHKsQAM"
      }
    ]
  },
  "id": "3fae6b87-9da0-4061-ad80-5b0e148a4290"
}
October 7, 2021 10:02 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773815734099",
  "subject": "3773815734099",
  "time": "2021-10-07T14:02:55.6734984Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773815734099",
    "sourceDateTimeUtc": "2021-10-07T14:02:51+00:00",
    "stockNumber": "21334783",
    "reservationId": "06afbbea-983f-4e01-81aa-eea1d88ee6bf",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "114433",
        "meta": {
          "key": "locationId",
          "value": "6081"
        }
      },
      {
        "type": "crmId",
        "value": "0011C000032O6W4QAK"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~6JPSbnQ"
      },
      {
        "type": "ciamId",
        "value": "C6B9CAC9-74E6-4ACF-88B7-F6B5FDF8CEE7"
      }
    ]
  },
  "id": "de370443-da3b-4ad8-b2fa-6dad9d90e2de"
}
October 7, 2021 10:02 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593883836214",
  "subject": "1593883836214",
  "time": "2021-10-07T14:02:30.1436289Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593883836214",
    "sourceDateTimeUtc": "2021-10-07T14:02:10+00:00",
    "stockNumber": "21005796",
    "reservationId": "ae8a8ab7-4951-49e8-9bea-0b0c1693af33",
    "identity": [
      {
        "type": "ciamId",
        "value": "DD958CE7-AB33-4249-B23F-9A0764881B5A"
      },
      {
        "type": "storeCustomerId",
        "value": "435764",
        "meta": {
          "key": "locationId",
          "value": "7173"
        }
      }
    ]
  },
  "id": "0752074e-cd20-4a3e-ae9f-b7ef71af7b0b"
}
October 7, 2021 10:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516335574847",
  "subject": "2516335574847",
  "time": "2021-10-07T14:01:48.40362Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516335574847",
    "sourceDateTimeUtc": "2021-10-07T14:01:40+00:00",
    "stockNumber": "20378116",
    "reservationId": "54b4bfe4-5199-4687-ba6f-d69ede767f45",
    "identity": [
      {
        "type": "ciamId",
        "value": "1D1EB73B-0058-4E16-B028-9F5E01006F50"
      },
      {
        "type": "storeCustomerId",
        "value": "13189",
        "meta": {
          "key": "locationId",
          "value": "6141"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "f88e64e2-fbad-4b4b-a721-8e39916b42d7"
      },
      {
        "type": "crmId",
        "value": "0011C00002wZ72UQAS"
      }
    ]
  },
  "id": "10516288-8790-4dcf-b884-f1d64daaed14"
}
October 7, 2021 10:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812475072321",
  "subject": "812475072321",
  "time": "2021-10-07T14:01:42.7273859Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812475072321",
    "sourceDateTimeUtc": "2021-10-07T14:01:37+00:00",
    "stockNumber": "20614304",
    "reservationId": "52fee255-fd00-4c06-a3e1-f3ee8b4cbd2e",
    "identity": [
      {
        "type": "ciamId",
        "value": "7064FEA5-26C7-4279-90BF-60B806214E28"
      },
      {
        "type": "storeCustomerId",
        "value": "4469",
        "meta": {
          "key": "locationId",
          "value": "6149"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002xxlkOQAQ"
      },
      {
        "type": "buysCustomerId",
        "value": "f7344483-e826-4dbe-b87d-c8858f62eef2"
      }
    ]
  },
  "id": "8ad0ab1a-89ff-4336-b441-8a5c77a0cb7c"
}
October 7, 2021 10:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748071497539",
  "subject": "1748071497539",
  "time": "2021-10-07T14:01:07.424337Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748071497539",
    "sourceDateTimeUtc": "2021-10-07T14:01:01+00:00",
    "stockNumber": "20970180",
    "reservationId": "bb020d9f-391e-4ce3-b3e2-6b671cba17d5",
    "identity": [
      {
        "type": "ciamId",
        "value": "C36E6A7B-B350-4794-A5BE-84E7DDBCB493"
      },
      {
        "type": "storeCustomerId",
        "value": "137772",
        "meta": {
          "key": "locationId",
          "value": "6042"
        }
      }
    ]
  },
  "id": "a83aac83-cf7f-42a7-b36e-5d649e44a9f1"
}
October 7, 2021 10:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352342597448",
  "subject": "2352342597448",
  "time": "2021-10-07T14:00:59.9762705Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352342597448",
    "sourceDateTimeUtc": "2021-10-07T14:00:54+00:00",
    "stockNumber": "21109338",
    "reservationId": "89c0420e-ab06-4c22-87a0-a26ea46f52b0",
    "identity": [
      {
        "type": "ciamId",
        "value": "7361EC4A-50D4-4905-BC68-00080DEF0430"
      },
      {
        "type": "storeCustomerId",
        "value": "123187",
        "meta": {
          "key": "locationId",
          "value": "6031"
        }
      }
    ]
  },
  "id": "70307982-2087-4c0f-a283-a0c8059a4c9a"
}
October 7, 2021 10:00 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593882427190",
  "subject": "1593882427190",
  "time": "2021-10-07T14:00:24.9994804Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593882427190",
    "sourceDateTimeUtc": "2021-10-07T14:00:04+00:00",
    "stockNumber": "21050877",
    "reservationId": "d1838132-57db-4cd0-beb7-908827fb1255",
    "identity": [
      {
        "type": "ciamId",
        "value": "79CAB9A9-E6C9-418C-8C42-F7DD6E5AF929"
      },
      {
        "type": "storeCustomerId",
        "value": "324076",
        "meta": {
          "key": "locationId",
          "value": "7279"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036NNGKQA4"
      }
    ]
  },
  "id": "f40468e3-3c05-4c45-a6cd-fc49535a4d5c"
}
October 7, 2021 9:58 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096617520954",
  "subject": "2096617520954",
  "time": "2021-10-07T13:58:47.4154216Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096617520954",
    "sourceDateTimeUtc": "2021-10-07T13:58:43+00:00",
    "stockNumber": "19824267",
    "reservationId": "aa016697-908a-41e9-9e37-0cfdcde19681",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "28928",
        "meta": {
          "key": "locationId",
          "value": "6116"
        }
      },
      {
        "type": "ciamId",
        "value": "B22F5DA4-6DA8-4F68-9ED8-A5A90038A970"
      },
      {
        "type": "crmId",
        "value": "0011C00002fMz2dQAC"
      },
      {
        "type": "buysCustomerId",
        "value": "d9f26841-fceb-4767-87b7-c9914734f270"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~ZYdxSKu"
      }
    ]
  },
  "id": "e9678103-5dfc-4b4a-8b36-adb5780e838e"
}
October 7, 2021 9:58 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096617488186",
  "subject": "2096617488186",
  "time": "2021-10-07T13:58:43.9528365Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096617488186",
    "sourceDateTimeUtc": "2021-10-07T13:58:39+00:00",
    "stockNumber": "20979214",
    "reservationId": "af9794d1-8dc8-46ea-b789-5cebdb64fbdb",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "34706",
        "meta": {
          "key": "locationId",
          "value": "7255"
        }
      },
      {
        "type": "ciamId",
        "value": "C44CF449-6509-4288-B008-A3260404E56E"
      }
    ]
  },
  "id": "0f819924-4d20-4f11-a2d7-745f14fe31e8"
}
October 7, 2021 9:57 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593880985398",
  "subject": "1593880985398",
  "time": "2021-10-07T13:57:26.8410372Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593880985398",
    "sourceDateTimeUtc": "2021-10-07T13:57:18+00:00",
    "stockNumber": "21307552",
    "reservationId": "a132ab0c-5f3c-4138-842f-1b71dbabe17c",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002sUyCBQA0"
      },
      {
        "type": "cafCustomerId",
        "value": "0014335882"
      },
      {
        "type": "storeCustomerId",
        "value": "371022",
        "meta": {
          "key": "locationId",
          "value": "7203"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "444cc031-0b21-4790-95e3-369e7d3a08ba"
      },
      {
        "type": "ciamId",
        "value": "CC6B5FED-A5E6-4448-9D43-3C90A4A2F9F8"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~ULPkmFn"
      }
    ]
  },
  "id": "0b417315-5854-4351-b292-7770adeba442"
}
October 7, 2021 9:57 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390426771279",
  "subject": "4390426771279",
  "time": "2021-10-07T13:57:11.4144939Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390426771279",
    "sourceDateTimeUtc": "2021-10-07T13:57:07+00:00",
    "stockNumber": "20449868",
    "reservationId": "450e9cc7-5a4f-41fd-a4fb-22dd1cf7e422",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "ed9725fd-4304-4ba7-9c7b-136463f7bde9"
      },
      {
        "type": "storeCustomerId",
        "value": "78351",
        "meta": {
          "key": "locationId",
          "value": "6043"
        }
      },
      {
        "type": "ciamId",
        "value": "F84DFA62-186E-4D9D-B894-4A38B5C5D09C"
      },
      {
        "type": "crmId",
        "value": "0011C00002mzVseQAE"
      }
    ]
  },
  "id": "0536f707-ac3b-4ce7-87fa-b400d1c7a488"
}
October 7, 2021 9:54 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516331560767",
  "subject": "2516331560767",
  "time": "2021-10-07T13:54:54.3577696Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516331560767",
    "sourceDateTimeUtc": "2021-10-07T13:54:45+00:00",
    "stockNumber": "20590869",
    "reservationId": "11c22245-3da9-461e-9f0c-df9b465fc5f4",
    "identity": [
      {
        "type": "ciamId",
        "value": "FB961D6E-E8EA-448E-A386-97448BE16C2A"
      },
      {
        "type": "storeCustomerId",
        "value": "795173",
        "meta": {
          "key": "locationId",
          "value": "7810"
        }
      }
    ]
  },
  "id": "857d28c8-6d3f-4061-b853-8bc309d71f1d"
}
October 7, 2021 9:54 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390425018191",
  "subject": "4390425018191",
  "time": "2021-10-07T13:54:54.3481582Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390425018191",
    "sourceDateTimeUtc": "2021-10-07T13:54:48+00:00",
    "stockNumber": "21191568",
    "reservationId": "2e033261-02a4-48ad-a1b2-1c85894f7359",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000035AsszQAC"
      },
      {
        "type": "storeCustomerId",
        "value": "435762",
        "meta": {
          "key": "locationId",
          "value": "7173"
        }
      },
      {
        "type": "ciamId",
        "value": "16D12813-A8FF-4DF3-A43C-5971A099B397"
      }
    ]
  },
  "id": "fb97d857-c9d8-489d-9535-4191883c53e4"
}
October 7, 2021 9:54 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390424887119",
  "subject": "4390424887119",
  "time": "2021-10-07T13:54:37.8888533Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390424887119",
    "sourceDateTimeUtc": "2021-10-07T13:54:33+00:00",
    "stockNumber": "21132885",
    "reservationId": "04e4a584-36f0-4354-a7b9-501911e3ce69",
    "identity": [
      {
        "type": "ciamId",
        "value": "7064FEA5-26C7-4279-90BF-60B806214E28"
      },
      {
        "type": "storeCustomerId",
        "value": "44839",
        "meta": {
          "key": "locationId",
          "value": "6020"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002xxlkOQAQ"
      },
      {
        "type": "buysCustomerId",
        "value": "f7344483-e826-4dbe-b87d-c8858f62eef2"
      }
    ]
  },
  "id": "2987b199-7df2-461d-9708-d70d48901d89"
}
October 7, 2021 9:54 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773810212691",
  "subject": "3773810212691",
  "time": "2021-10-07T13:54:24.0078414Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773810212691",
    "sourceDateTimeUtc": "2021-10-07T13:54:19+00:00",
    "stockNumber": "20263807",
    "reservationId": "e5286f61-0676-4841-8de6-1a5e879201e8",
    "identity": [
      {
        "type": "ciamId",
        "value": "83303C35-403C-4B91-BD07-A40A00E5900D"
      },
      {
        "type": "crmId",
        "value": "0016R000035ruw4QAA"
      },
      {
        "type": "storeCustomerId",
        "value": "330325",
        "meta": {
          "key": "locationId",
          "value": "7243"
        }
      }
    ]
  },
  "id": "83410615-6227-4a94-adb2-37f7a9d75d33"
}
October 7, 2021 9:52 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748067794755",
  "subject": "1748067794755",
  "time": "2021-10-07T13:52:58.1791134Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748067794755",
    "sourceDateTimeUtc": "2021-10-07T13:52:50+00:00",
    "stockNumber": "21028649",
    "reservationId": "29eb5bfc-8617-4dbb-9014-a63476866a5b",
    "identity": [
      {
        "type": "ciamId",
        "value": "694CF99C-0933-4C2D-A2C1-ED18F65F7C2B"
      },
      {
        "type": "storeCustomerId",
        "value": "61993",
        "meta": {
          "key": "locationId",
          "value": "6110"
        }
      }
    ]
  },
  "id": "4f8841c6-9a57-423a-9d16-d32332128026"
}
October 7, 2021 9:52 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390424035151",
  "subject": "4390424035151",
  "time": "2021-10-07T13:52:38.4966926Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390424035151",
    "sourceDateTimeUtc": "2021-10-07T13:52:20+00:00",
    "stockNumber": "21353320",
    "reservationId": "61bb8303-c5e7-42de-8a6e-8553ca8a1f59",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C000033qjLEQAY"
      },
      {
        "type": "ciamId",
        "value": "2428EA97-4166-46E1-AC5B-A1B616423B1B"
      },
      {
        "type": "storeCustomerId",
        "value": "898363",
        "meta": {
          "key": "locationId",
          "value": "7102"
        }
      }
    ]
  },
  "id": "250a2587-fff2-4364-ba1e-6bf6d42381f4"
}
October 7, 2021 9:51 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516329676607",
  "subject": "2516329676607",
  "time": "2021-10-07T13:51:22.0472218Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516329676607",
    "sourceDateTimeUtc": "2021-10-07T13:51:14+00:00",
    "stockNumber": "20499287",
    "reservationId": "b4bad961-f2e0-4121-9c41-44590db06ab1",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "99360",
        "meta": {
          "key": "locationId",
          "value": "7165"
        }
      },
      {
        "type": "ciamId",
        "value": "FF8A2EC6-6364-4683-AB5A-7BA49CFB42FC"
      }
    ]
  },
  "id": "c5aae6ee-c2a8-441e-8d62-3661accefe51"
}
October 7, 2021 9:51 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773808230227",
  "subject": "3773808230227",
  "time": "2021-10-07T13:51:07.5250962Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773808230227",
    "sourceDateTimeUtc": "2021-10-07T13:51:02+00:00",
    "stockNumber": "21331945",
    "reservationId": "28b74a8f-78bf-4d8b-a18d-853981e82106",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R0000360ZYYQA2"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~O1nazmP"
      },
      {
        "type": "buysCustomerId",
        "value": "cb838912-822f-4d33-9fa4-c0a144a1bb75"
      },
      {
        "type": "ciamId",
        "value": "CE2B02FD-1765-4532-8B78-F97CC2DE38D4"
      },
      {
        "type": "storeCustomerId",
        "value": "625292",
        "meta": {
          "key": "locationId",
          "value": "7105"
        }
      }
    ]
  },
  "id": "c9178329-0aba-4822-ab70-c81251f4c4f5"
}
October 7, 2021 9:51 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748067008323",
  "subject": "1748067008323",
  "time": "2021-10-07T13:51:03.7587933Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748067008323",
    "sourceDateTimeUtc": "2021-10-07T13:51:01+00:00",
    "stockNumber": "20953948",
    "reservationId": "83de23a2-5667-4dc4-a0a4-4cdec424c85b",
    "identity": [
      {
        "type": "ciamId",
        "value": "2F4F365A-6202-4103-A526-60A92E78F00A"
      },
      {
        "type": "crmId",
        "value": "0016R000036ObWrQAK"
      },
      {
        "type": "buysCustomerId",
        "value": "93a013a1-0054-4763-8e08-7cbff6538444"
      }
    ]
  },
  "id": "0f4dee6a-2238-4fe9-9643-79c9f74e5fcd"
}
October 7, 2021 9:50 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390422904655",
  "subject": "4390422904655",
  "time": "2021-10-07T13:50:16.9456676Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390422904655",
    "sourceDateTimeUtc": "2021-10-07T13:50:08+00:00",
    "stockNumber": "21131160",
    "reservationId": "68e84f92-4471-4d11-b6c7-32c6b296ad07",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000035f3XzQAI"
      },
      {
        "type": "buysCustomerId",
        "value": "d6aa5f7e-6a80-4533-9876-9eec9e445c9b"
      },
      {
        "type": "storeCustomerId",
        "value": "112294",
        "meta": {
          "key": "locationId",
          "value": "6025"
        }
      },
      {
        "type": "ciamId",
        "value": "BF572542-A3A4-4BAC-9841-417DA27FB214"
      }
    ]
  },
  "id": "32fb314f-911a-441a-b99e-67ece69fa335"
}
October 7, 2021 9:49 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988475924283",
  "subject": "2988475924283",
  "time": "2021-10-07T13:49:19.3360751Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988475924283",
    "sourceDateTimeUtc": "2021-10-07T13:49:09+00:00",
    "stockNumber": "21166897",
    "reservationId": "366c2233-f678-4e8d-a8f4-7d144a060f84",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "111410",
        "meta": {
          "key": "locationId",
          "value": "7290"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002sVT2WQAW"
      },
      {
        "type": "ciamId",
        "value": "B9FF9390-DD60-427A-8DDA-9A3C50BFAF5C"
      },
      {
        "type": "buysCustomerId",
        "value": "5c861b74-159a-4a27-9e63-e91c0fbab8db"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~vSfd0Qy"
      }
    ]
  },
  "id": "1f2139d2-189e-48d3-9ba3-4e982b7623e4"
}
October 7, 2021 9:48 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390421806927",
  "subject": "4390421806927",
  "time": "2021-10-07T13:48:09.8165874Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390421806927",
    "sourceDateTimeUtc": "2021-10-07T13:48:06+00:00",
    "stockNumber": "21332527",
    "reservationId": "8d98422c-a29b-46b8-a749-bb5513b3baaf",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "711766",
        "meta": {
          "key": "locationId",
          "value": "7152"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "d6f5bbf8-9520-4d97-b071-faabc4036c1c"
      },
      {
        "type": "ciamId",
        "value": "7E56EFE9-9F47-496E-9921-0F7F64BB8837"
      },
      {
        "type": "crmId",
        "value": "0016R000036O7cMQAS"
      }
    ]
  },
  "id": "7e233b95-3ddd-4ffa-a541-a81e9924f487"
}
October 7, 2021 9:48 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096613113658",
  "subject": "2096613113658",
  "time": "2021-10-07T13:48:09.8086491Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096613113658",
    "sourceDateTimeUtc": "2021-10-07T13:48:04+00:00",
    "stockNumber": "21184995",
    "reservationId": "dc802a67-1e36-4b44-aadf-d7520c9ce1e5",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "125749",
        "meta": {
          "key": "locationId",
          "value": "6072"
        }
      },
      {
        "type": "ciamId",
        "value": "DF9D0BC0-FF7C-419F-9FC3-3BD66DCAC7E7"
      },
      {
        "type": "crmId",
        "value": "0016R000036OYNzQAO"
      }
    ]
  },
  "id": "959df53d-5d91-440e-ba6f-b7c440de8f62"
}
October 7, 2021 9:48 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773807148883",
  "subject": "3773807148883",
  "time": "2021-10-07T13:48:02.7448704Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773807148883",
    "sourceDateTimeUtc": "2021-10-07T13:47:55+00:00",
    "stockNumber": "21117049",
    "reservationId": "503a4bb5-deaf-45e6-8aad-861649a1ca50",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "711764",
        "meta": {
          "key": "locationId",
          "value": "7152"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~VK2DJQ1"
      },
      {
        "type": "crmId",
        "value": "0011C00002lzLPHQA2"
      },
      {
        "type": "buysCustomerId",
        "value": "4b7bbdf1-48e4-42e6-865e-c2e42cf4495c"
      },
      {
        "type": "cafCustomerId",
        "value": "0014340761"
      },
      {
        "type": "ciamId",
        "value": "85D5911D-A53C-479F-B87C-E602AFB18FB3"
      }
    ]
  },
  "id": "93dd9bb8-c538-463c-8f69-f1c008a954eb"
}
October 7, 2021 9:48 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748065402691",
  "subject": "1748065402691",
  "time": "2021-10-07T13:48:03.20721Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748065402691",
    "sourceDateTimeUtc": "2021-10-07T13:47:50+00:00",
    "stockNumber": "21319233",
    "reservationId": "8423847a-e75d-40da-9780-662080c6389f",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "164973",
        "meta": {
          "key": "locationId",
          "value": "7201"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002ar3NNQAY"
      },
      {
        "type": "buysCustomerId",
        "value": "2d74ebf1-3bec-446e-a0e0-e7c6a4381571"
      },
      {
        "type": "ciamId",
        "value": "B498E113-F677-4421-9FE0-BFDC928B068A"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~12mdJsWi"
      }
    ]
  },
  "id": "7096692a-237f-4699-b748-61af9f286867"
}
October 7, 2021 9:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352336355144",
  "subject": "2352336355144",
  "time": "2021-10-07T13:47:30.5328918Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352336355144",
    "sourceDateTimeUtc": "2021-10-07T13:47:25+00:00",
    "stockNumber": "20864107",
    "reservationId": "8eecc907-0b21-4966-8623-71724d06ab24",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "fe9b99f8-2f35-4147-8b4c-58f2544bab6a"
      },
      {
        "type": "crmId",
        "value": "0011C00002ofzayQAA"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~Vu2Fysi"
      },
      {
        "type": "storeCustomerId",
        "value": "298161",
        "meta": {
          "key": "locationId",
          "value": "7283"
        }
      },
      {
        "type": "ciamId",
        "value": "C79A6854-B227-40A2-BCDE-A660009EABF8"
      }
    ]
  },
  "id": "26f6cc9e-1943-4a36-b609-a3fa5b41eb91"
}
October 7, 2021 9:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352336109384",
  "subject": "2352336109384",
  "time": "2021-10-07T13:47:13.1804423Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352336109384",
    "sourceDateTimeUtc": "2021-10-07T13:47:06+00:00",
    "stockNumber": "21132427",
    "reservationId": "459dd894-e7c3-4243-9c2f-d0b3d97bb732",
    "identity": [
      {
        "type": "ciamId",
        "value": "12A0EF3A-AE2C-47C3-AB7A-D0D0B08B9556"
      },
      {
        "type": "storeCustomerId",
        "value": "115625",
        "meta": {
          "key": "locationId",
          "value": "6036"
        }
      }
    ]
  },
  "id": "bfd3b674-ad35-48fe-9dbe-b06283c94cc5"
}
October 7, 2021 9:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773806280531",
  "subject": "3773806280531",
  "time": "2021-10-07T13:46:59.4449251Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773806280531",
    "sourceDateTimeUtc": "2021-10-07T13:46:11+00:00",
    "stockNumber": "21332727",
    "reservationId": "8813bb1b-005c-4ca4-ab36-2b004d6085a3",
    "identity": [
      {
        "type": "cafCustomerId",
        "value": "0014189839"
      },
      {
        "type": "storeCustomerId",
        "value": "711763",
        "meta": {
          "key": "locationId",
          "value": "7152"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~MM1EixC"
      },
      {
        "type": "buysCustomerId",
        "value": "6ffe7003-9bd0-4c16-bbdd-cff0b34db297"
      },
      {
        "type": "crmId",
        "value": "0011C00002nZcnhQAC"
      },
      {
        "type": "ciamId",
        "value": "51D8C0AD-6104-4963-A87E-0358026D9331"
      }
    ]
  },
  "id": "a1da3e14-ecfa-4f89-bcd1-f57b9e05f20e"
}
October 7, 2021 9:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516327595839",
  "subject": "2516327595839",
  "time": "2021-10-07T13:46:57.6858829Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516327595839",
    "sourceDateTimeUtc": "2021-10-07T13:46:53+00:00",
    "stockNumber": "20860244",
    "reservationId": "60aad5fe-f939-4375-b7be-d7c4e6d3d138",
    "identity": [
      {
        "type": "ciamId",
        "value": "2B2E56C1-5DC5-4857-BE79-4B17207571CC"
      },
      {
        "type": "storeCustomerId",
        "value": "111408",
        "meta": {
          "key": "locationId",
          "value": "7290"
        }
      }
    ]
  },
  "id": "32d835c1-fcb9-452b-be62-41a5ca468e2c"
}
October 7, 2021 9:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390419791695",
  "subject": "4390419791695",
  "time": "2021-10-07T13:46:06.0638848Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390419791695",
    "sourceDateTimeUtc": "2021-10-07T13:45:58+00:00",
    "stockNumber": "20827284",
    "reservationId": "aff2a95e-6129-42c2-9948-722b3696d3b2",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "649459",
        "meta": {
          "key": "locationId",
          "value": "7206"
        }
      },
      {
        "type": "ciamId",
        "value": "07138C25-16C0-43B3-AD08-B83441BCF568"
      }
    ]
  },
  "id": "d1ccb094-5e37-4d34-8699-af8834ffa90b"
}
October 7, 2021 9:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773805330259",
  "subject": "3773805330259",
  "time": "2021-10-07T13:46:01.8248319Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773805330259",
    "sourceDateTimeUtc": "2021-10-07T13:45:57+00:00",
    "stockNumber": "20879505",
    "reservationId": "017181a5-e452-4e8d-9b06-4f6c365ef210",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "641687",
        "meta": {
          "key": "locationId",
          "value": "7167"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObYdQAK"
      },
      {
        "type": "ciamId",
        "value": "28F540D3-2A02-4F61-85F8-BE388F21BA1B"
      }
    ]
  },
  "id": "f47ad8dd-e7a7-47d6-9e3a-96d8b1b240fa"
}
October 7, 2021 9:45 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593874923318",
  "subject": "1593874923318",
  "time": "2021-10-07T13:45:56.7255722Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593874923318",
    "sourceDateTimeUtc": "2021-10-07T13:45:50+00:00",
    "stockNumber": "20535092",
    "reservationId": "d44dad22-0ba0-4ee5-ad84-3f2c19046428",
    "identity": [
      {
        "type": "ciamId",
        "value": "3812EBEE-C745-4B23-965F-EF4DE2871647"
      },
      {
        "type": "storeCustomerId",
        "value": "400553",
        "meta": {
          "key": "locationId",
          "value": "7185"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00001u1ai8QAA"
      }
    ]
  },
  "id": "155783e7-39c6-4761-b957-39cb1469271e"
}
October 7, 2021 9:45 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390419726159",
  "subject": "4390419726159",
  "time": "2021-10-07T13:45:46.3243124Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390419726159",
    "sourceDateTimeUtc": "2021-10-07T13:45:39+00:00",
    "stockNumber": "20899700",
    "reservationId": "73657ebc-ebc9-4ec8-a2a2-734ea651cb70",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "115179",
        "meta": {
          "key": "locationId",
          "value": "6025"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002MX0CRQA1"
      },
      {
        "type": "ciamId",
        "value": "21B0A37A-C996-41DC-8E8E-3C6326392248"
      }
    ]
  },
  "id": "cd4f2708-a4ba-44e0-983d-ae7d5cc4d2b7"
}
October 7, 2021 9:45 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593874628406",
  "subject": "1593874628406",
  "time": "2021-10-07T13:45:23.3898338Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593874628406",
    "sourceDateTimeUtc": "2021-10-07T13:45:20+00:00",
    "stockNumber": "21219269",
    "reservationId": "fe528f5c-b3b0-4207-8bb2-8b2d050d4265",
    "identity": [
      {
        "type": "ciamId",
        "value": "BE9D8EF4-E8FC-4A70-9E04-A57D00BBBF35"
      },
      {
        "type": "buysCustomerId",
        "value": "053065c0-6346-4376-a8d0-93c8e60486f7"
      },
      {
        "type": "crmId",
        "value": "0016R000036ObQ6QAK"
      }
    ]
  },
  "id": "74b9a43b-9150-474b-bdd3-5234dff1b0c8"
}
October 7, 2021 9:45 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773804330835",
  "subject": "3773804330835",
  "time": "2021-10-07T13:45:01.7487609Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773804330835",
    "sourceDateTimeUtc": "2021-10-07T13:44:56+00:00",
    "stockNumber": "20531504",
    "reservationId": "6c9e615d-5535-487a-ac16-2f777736d8f8",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "627758",
        "meta": {
          "key": "locationId",
          "value": "7105"
        }
      },
      {
        "type": "crmId",
        "value": "0016R0000358yX3QAI"
      },
      {
        "type": "ciamId",
        "value": "2736A86E-FB5B-4906-B3D8-A4450129BCAE"
      },
      {
        "type": "buysCustomerId",
        "value": "153bed95-84b3-42cd-9189-ea5e127dc250"
      }
    ]
  },
  "id": "69cda403-3118-4dc3-9e5e-db8030195c1d"
}
October 7, 2021 9:43 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988471123771",
  "subject": "2988471123771",
  "time": "2021-10-07T13:43:00.6617618Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988471123771",
    "sourceDateTimeUtc": "2021-10-07T13:42:48+00:00",
    "stockNumber": "20985638",
    "reservationId": "0c2cfcd9-fdd5-4307-840d-afd7594ea027",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "295364",
        "meta": {
          "key": "locationId",
          "value": "7190"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "4cb8fe23-1822-48b8-80a9-dcd37b804575"
      },
      {
        "type": "ciamId",
        "value": "C2373E06-3484-4CF1-B7A1-D9140F91834B"
      },
      {
        "type": "crmId",
        "value": "0016R000035f3hDQAQ"
      }
    ]
  },
  "id": "33039865-a396-452a-be87-e49ccdad779a"
}
October 7, 2021 9:41 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812465749825",
  "subject": "812465749825",
  "time": "2021-10-07T13:41:49.0863427Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812465749825",
    "sourceDateTimeUtc": "2021-10-07T13:41:43+00:00",
    "stockNumber": "21138895",
    "reservationId": "c88b786e-33f2-4a7d-bb00-776a62ac8bd9",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036OMBuQAO"
      },
      {
        "type": "storeCustomerId",
        "value": "105319",
        "meta": {
          "key": "locationId",
          "value": "7285"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "1dc58b55-582c-43f1-ab2f-cf6b68ac8cb9"
      },
      {
        "type": "ciamId",
        "value": "D41B8E13-E511-4234-8F1E-44F48FA947F9"
      }
    ]
  },
  "id": "0e359fdc-6e24-424a-b6e9-499af69c4271"
}
October 7, 2021 9:41 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773802774355",
  "subject": "3773802774355",
  "time": "2021-10-07T13:41:35.1204833Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773802774355",
    "sourceDateTimeUtc": "2021-10-07T13:41:23+00:00",
    "stockNumber": "20971184",
    "reservationId": "3fc104f1-e2d0-44db-818f-3c9f60d8e0ed",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "512655",
        "meta": {
          "key": "locationId",
          "value": "7150"
        }
      },
      {
        "type": "cafCustomerId",
        "value": "0014395227"
      },
      {
        "type": "crmId",
        "value": "0016R000034MYSjQAO"
      },
      {
        "type": "buysCustomerId",
        "value": "1a622854-44cc-4a99-aefa-c3b608d3ff9e"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~72H0Ywa"
      },
      {
        "type": "ciamId",
        "value": "73877B0D-E228-4450-B110-DCCA5B35F736"
      }
    ]
  },
  "id": "c7c43723-6ddb-4177-8222-2aae3e7b65e9"
}
October 7, 2021 9:41 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096608886586",
  "subject": "2096608886586",
  "time": "2021-10-07T13:41:16.4116407Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096608886586",
    "sourceDateTimeUtc": "2021-10-07T13:40:59+00:00",
    "stockNumber": "21268897",
    "reservationId": "bc0e80f9-aaec-4ca1-a1a9-c2011b15d0ee",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002uzVLtQAM"
      },
      {
        "type": "storeCustomerId",
        "value": "62765",
        "meta": {
          "key": "locationId",
          "value": "6013"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "d66ec3a9-d05f-402d-aff0-697e1171d6fb"
      },
      {
        "type": "ciamId",
        "value": "7629D855-311D-4BDB-BE3E-76578381CB76"
      }
    ]
  },
  "id": "2b162248-ee45-4eb3-9460-b73240f552fd"
}
October 7, 2021 9:40 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593871597366",
  "subject": "1593871597366",
  "time": "2021-10-07T13:40:00.7914407Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593871597366",
    "sourceDateTimeUtc": "2021-10-07T13:39:50+00:00",
    "stockNumber": "20466767",
    "reservationId": "4f114515-6ec3-4e0b-87ed-2cfcce9d6524",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "757842",
        "meta": {
          "key": "locationId",
          "value": "7147"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "c0735486-c60f-42a7-955e-fddeefa7a53f"
      },
      {
        "type": "crmId",
        "value": "0011C00002nj6xBQAQ"
      },
      {
        "type": "ciamId",
        "value": "89AC2C73-FE09-4976-B331-1AC66DA8A059"
      }
    ]
  },
  "id": "f5914fe9-7e44-4fb9-8395-16e283dc05e9"
}
October 7, 2021 9:38 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773801840467",
  "subject": "3773801840467",
  "time": "2021-10-07T13:38:56.9045252Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773801840467",
    "sourceDateTimeUtc": "2021-10-07T13:38:49+00:00",
    "stockNumber": "21353168",
    "reservationId": "6260b61c-dd25-40d9-977d-fc99c05e350c",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "898357",
        "meta": {
          "key": "locationId",
          "value": "7102"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002apyyCQAQ"
      },
      {
        "type": "buysCustomerId",
        "value": "3bd350de-adee-4f0c-924e-efb24e2f9b25"
      },
      {
        "type": "ciamId",
        "value": "59C7241C-01C2-42D4-82B6-096981291B00"
      },
      {
        "type": "cafCustomerId",
        "value": "0013768164"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~11n6ZszN"
      }
    ]
  },
  "id": "1bb28670-bca9-49bc-ad16-60d9b029bc7b"
}
October 7, 2021 9:37 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390415974223",
  "subject": "4390415974223",
  "time": "2021-10-07T13:37:43.2461968Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390415974223",
    "sourceDateTimeUtc": "2021-10-07T13:37:39+00:00",
    "stockNumber": "20908151",
    "reservationId": "f6b863ca-6d29-496a-b955-12e6b18920e4",
    "identity": [
      {
        "type": "ciamId",
        "value": "09D38B21-7DED-46BE-8670-DE96BDEFDBE0"
      },
      {
        "type": "buysCustomerId",
        "value": "7e3dc9b3-7f67-47a6-aa9f-4779ca9e22bb"
      },
      {
        "type": "storeCustomerId",
        "value": "135483",
        "meta": {
          "key": "locationId",
          "value": "6001"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000035ow1MQAQ"
      }
    ]
  },
  "id": "abca0dc3-1a32-4b92-a920-da654dc70867"
}
October 7, 2021 9:36 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352329719624",
  "subject": "2352329719624",
  "time": "2021-10-07T13:36:41.2933827Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352329719624",
    "sourceDateTimeUtc": "2021-10-07T13:36:32+00:00",
    "stockNumber": "20989858",
    "reservationId": "35e0ccd5-3bb4-4da0-9cb4-a5cbbd5122b0",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "550806",
        "meta": {
          "key": "locationId",
          "value": "7154"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036NtMVQA0"
      },
      {
        "type": "ciamId",
        "value": "0DA034EE-56FC-4964-8257-CB6839F7C296"
      },
      {
        "type": "buysCustomerId",
        "value": "c14e9850-d066-4794-962a-e0aea32775c1"
      }
    ]
  },
  "id": "b41d223c-d21f-4b6b-ae58-e182fcabdba7"
}
October 7, 2021 9:36 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516321271615",
  "subject": "2516321271615",
  "time": "2021-10-07T13:36:15.6229072Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516321271615",
    "sourceDateTimeUtc": "2021-10-07T13:36:00+00:00",
    "stockNumber": "21181254",
    "reservationId": "d095f47f-9dd0-41c5-a0ef-29a634f3cd00",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "4bb480a6-dfaa-4faf-859b-3ce8aa987b63"
      },
      {
        "type": "ciamId",
        "value": "45D9DCBF-6C97-4936-A51B-9F1800E76C55"
      },
      {
        "type": "storeCustomerId",
        "value": "379293",
        "meta": {
          "key": "locationId",
          "value": "7130"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~14KDWash"
      },
      {
        "type": "crmId",
        "value": "0011C00002yWKQtQAO"
      },
      {
        "type": "cafCustomerId",
        "value": "0013995298"
      }
    ]
  },
  "id": "a7668689-c642-4f1b-9d23-d4b38bfd9640"
}
October 7, 2021 9:36 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773800038227",
  "subject": "3773800038227",
  "time": "2021-10-07T13:36:15.6144439Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773800038227",
    "sourceDateTimeUtc": "2021-10-07T13:36:08+00:00",
    "stockNumber": "21002029",
    "reservationId": "2641d505-4f66-4eb3-801f-97e867d7ed78",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "1617e5ae-2880-41af-aff8-d6cf3c08b352"
      },
      {
        "type": "storeCustomerId",
        "value": "45586",
        "meta": {
          "key": "locationId",
          "value": "6070"
        }
      },
      {
        "type": "ciamId",
        "value": "596243A8-9ECE-468E-B478-36D49588B880"
      },
      {
        "type": "crmId",
        "value": "0016R000035rWIZQA2"
      }
    ]
  },
  "id": "7e2f004d-c00e-4530-8da0-7cc385147c85"
}
October 7, 2021 9:34 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748056227651",
  "subject": "1748056227651",
  "time": "2021-10-07T13:34:51.7620332Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748056227651",
    "sourceDateTimeUtc": "2021-10-07T13:34:37+00:00",
    "stockNumber": "21223866",
    "reservationId": "c0a699ee-ccc0-48da-b42a-2dc74fa3e410",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "203112",
        "meta": {
          "key": "locationId",
          "value": "7201"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "2402ed0f-0750-4bf7-a9cc-fac7ac234428"
      },
      {
        "type": "crmId",
        "value": "0016R000036OOM1QAO"
      },
      {
        "type": "ciamId",
        "value": "2F9BEBB9-4FAD-4FD6-9C43-438FBC9A476D"
      }
    ]
  },
  "id": "9cc24d00-b7e9-4b3f-8a36-bca6dbae1d05"
}
October 7, 2021 9:33 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748052983619",
  "subject": "1748052983619",
  "time": "2021-10-07T13:33:19.5042953Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748052983619",
    "sourceDateTimeUtc": "2021-10-07T13:33:14+00:00",
    "stockNumber": "21142425",
    "reservationId": "f412beae-58f6-439c-9a1a-b945e60e4ac7",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "166024",
        "meta": {
          "key": "locationId",
          "value": "7282"
        }
      },
      {
        "type": "ciamId",
        "value": "18ED6D72-CF4B-4D08-AF3E-5E3FC61F236D"
      },
      {
        "type": "crmId",
        "value": "0016R000036OVw2QAG"
      },
      {
        "type": "buysCustomerId",
        "value": "82cc6f36-6887-47de-8ca9-8e108187b50c"
      }
    ]
  },
  "id": "5e29e94b-f691-4725-80d5-5d46bd9c640a"
}
October 7, 2021 9:32 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390408716111",
  "subject": "4390408716111",
  "time": "2021-10-07T13:32:32.2100338Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390408716111",
    "sourceDateTimeUtc": "2021-10-07T13:32:22+00:00",
    "stockNumber": "21035434",
    "reservationId": "525da85b-d621-474a-a754-6f42d03425c3",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "116931",
        "meta": {
          "key": "locationId",
          "value": "7280"
        }
      },
      {
        "type": "ciamId",
        "value": "515D5BC6-D1F0-4F71-8AB1-34647C5BBABE"
      }
    ]
  },
  "id": "6f5a9891-a4fb-41a8-930b-2fa2165662dd"
}
October 7, 2021 9:31 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748048772931",
  "subject": "1748048772931",
  "time": "2021-10-07T13:31:18.7769428Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748048772931",
    "sourceDateTimeUtc": "2021-10-07T13:31:14+00:00",
    "stockNumber": "20641300",
    "reservationId": "caac8c12-5205-46b3-9293-be3d9353be49",
    "identity": [
      {
        "type": "cafCustomerId",
        "value": "0013066573"
      },
      {
        "type": "storeCustomerId",
        "value": "299671",
        "meta": {
          "key": "locationId",
          "value": "7242"
        }
      },
      {
        "type": "ciamId",
        "value": "F631BE67-C72D-4E93-845B-710237EDEAB8"
      },
      {
        "type": "buysCustomerId",
        "value": "695ffdfa-e94a-448f-9ec4-368d494fb7aa"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~VTtiIjp"
      },
      {
        "type": "crmId",
        "value": "0011C00002WWJbdQAH"
      }
    ]
  },
  "id": "21d24aa6-81f9-4439-ad3b-cf7b4d9f5267"
}
October 7, 2021 9:31 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812452986689",
  "subject": "812452986689",
  "time": "2021-10-07T13:31:03.2985283Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812452986689",
    "sourceDateTimeUtc": "2021-10-07T13:30:59+00:00",
    "stockNumber": "21142098",
    "reservationId": "f87022b6-78df-489d-ae20-64e0e53b728d",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "166023",
        "meta": {
          "key": "locationId",
          "value": "7282"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "888001d6-97da-4188-8a88-a5caca05df7a"
      },
      {
        "type": "ciamId",
        "value": "233B4807-9B25-418C-9F83-2FA46160A69C"
      },
      {
        "type": "crmId",
        "value": "0011C000025hR3FQAU"
      }
    ]
  },
  "id": "82c9ce2a-a308-4271-acc1-94ac06c86afb"
}
October 7, 2021 9:29 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988455558971",
  "subject": "2988455558971",
  "time": "2021-10-07T13:29:26.6910563Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988455558971",
    "sourceDateTimeUtc": "2021-10-07T13:29:17+00:00",
    "stockNumber": "21196581",
    "reservationId": "b608eb2a-de9f-4d97-a0a3-cb39f7690c09",
    "identity": [
      {
        "type": "ciamId",
        "value": "AED36921-0B06-4F10-90BF-0E8FC2E306F6"
      },
      {
        "type": "crmId",
        "value": "0016R000036OI6WQAW"
      },
      {
        "type": "storeCustomerId",
        "value": "634186",
        "meta": {
          "key": "locationId",
          "value": "7120"
        }
      }
    ]
  },
  "id": "858504b2-2b8d-4caf-8720-c15b983f945f"
}
October 7, 2021 9:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390399475535",
  "subject": "4390399475535",
  "time": "2021-10-07T13:28:53.4076685Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390399475535",
    "sourceDateTimeUtc": "2021-10-07T13:28:47+00:00",
    "stockNumber": "21004368",
    "reservationId": "6d28bf7f-a068-425e-a604-7dae9b65451e",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002Xpn9bQAB"
      },
      {
        "type": "ciamId",
        "value": "224EA9AC-41A2-4C4C-8601-5AA473178680"
      },
      {
        "type": "cafCustomerId",
        "value": "0011481365"
      }
    ]
  },
  "id": "91a7cd29-4358-4ec9-bfc0-451d85f388aa"
}
October 7, 2021 9:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812446449473",
  "subject": "812446449473",
  "time": "2021-10-07T13:28:23.1414037Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812446449473",
    "sourceDateTimeUtc": "2021-10-07T13:28:03+00:00",
    "stockNumber": "19223575",
    "reservationId": "14f85e54-e5b6-46ad-9bfd-0c169a8658e1",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "466c256c-0cc1-44a5-a2e3-a562d0ce08a6"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~6AJ3j4m"
      },
      {
        "type": "storeCustomerId",
        "value": "551181",
        "meta": {
          "key": "locationId",
          "value": "7195"
        }
      },
      {
        "type": "ciamId",
        "value": "4CA28F2E-6004-4930-A7F8-0F59E9DCC65D"
      },
      {
        "type": "crmId",
        "value": "0011C00002sUhg0QAC"
      }
    ]
  },
  "id": "e5c7dfaa-6a3f-421b-b1d6-ed5b9c08f426"
}
October 7, 2021 9:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812445073217",
  "subject": "812445073217",
  "time": "2021-10-07T13:28:12.0684784Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812445073217",
    "sourceDateTimeUtc": "2021-10-07T13:27:29+00:00",
    "stockNumber": "21082506",
    "reservationId": "9db04c63-e3ba-40a7-98cf-f1fe51a2a834",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "320855",
        "meta": {
          "key": "locationId",
          "value": "7243"
        }
      },
      {
        "type": "crmId",
        "value": "0011C000021PsKyQAK"
      },
      {
        "type": "buysCustomerId",
        "value": "83ea587c-c489-45cf-9980-8c90d7917da5"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~kvvk4T8"
      },
      {
        "type": "ciamId",
        "value": "69813300-D40C-4EC3-A98B-B69CBB326177"
      }
    ]
  },
  "id": "b7d373e6-ca8f-41aa-a87c-ebd9c4e8a798"
}
October 7, 2021 9:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390397738831",
  "subject": "4390397738831",
  "time": "2021-10-07T13:28:10.0924495Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390397738831",
    "sourceDateTimeUtc": "2021-10-07T13:27:59+00:00",
    "stockNumber": "20762342",
    "reservationId": "f8ca235c-80d5-4372-bedb-45aaeac6a8b0",
    "identity": [
      {
        "type": "ciamId",
        "value": "16E406D7-8A09-45DF-A396-EEB80F989F33"
      },
      {
        "type": "storeCustomerId",
        "value": "245108",
        "meta": {
          "key": "locationId",
          "value": "7284"
        }
      }
    ]
  },
  "id": "a086d623-e84b-43e4-8975-b1b039d408ef"
}
October 7, 2021 9:27 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988450332475",
  "subject": "2988450332475",
  "time": "2021-10-07T13:27:14.3111318Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988450332475",
    "sourceDateTimeUtc": "2021-10-07T13:27:05+00:00",
    "stockNumber": "21106647",
    "reservationId": "801ded88-a50f-4e65-adea-9ee9f4ec84ee",
    "identity": [
      {
        "type": "ciamId",
        "value": "229F05FD-7981-4692-BE9C-A21EA55FE75B"
      },
      {
        "type": "buysCustomerId",
        "value": "4c40c59f-764e-4b78-a75e-8b03d35ddd2a"
      },
      {
        "type": "crmId",
        "value": "0016R0000361172QAA"
      },
      {
        "type": "storeCustomerId",
        "value": "203110",
        "meta": {
          "key": "locationId",
          "value": "7201"
        }
      }
    ]
  },
  "id": "efdaedc6-a910-4b8d-b99e-896445cec326"
}
October 7, 2021 9:26 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516300382015",
  "subject": "2516300382015",
  "time": "2021-10-07T13:26:28.6824065Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516300382015",
    "sourceDateTimeUtc": "2021-10-07T13:26:25+00:00",
    "stockNumber": "21319491",
    "reservationId": "b87f776e-b7f3-4f53-9498-fecab30eea82",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "639984",
        "meta": {
          "key": "locationId",
          "value": "7101"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002apyyCQAQ"
      },
      {
        "type": "buysCustomerId",
        "value": "3bd350de-adee-4f0c-924e-efb24e2f9b25"
      },
      {
        "type": "ciamId",
        "value": "59C7241C-01C2-42D4-82B6-096981291B00"
      },
      {
        "type": "cafCustomerId",
        "value": "0013768164"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~11n6ZszN"
      }
    ]
  },
  "id": "0a5a9094-6f0e-46e2-9aea-bad4ef11530f"
}
October 7, 2021 9:24 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593845514038",
  "subject": "1593845514038",
  "time": "2021-10-07T13:24:40.5975969Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593845514038",
    "sourceDateTimeUtc": "2021-10-07T13:24:14+00:00",
    "stockNumber": "21320064",
    "reservationId": "9fa4a2bf-a16d-45be-8234-d1941a87636b",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "245107",
        "meta": {
          "key": "locationId",
          "value": "7284"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObgXQAS"
      },
      {
        "type": "ciamId",
        "value": "219629C1-B59F-47FD-879C-492E88499881"
      }
    ]
  },
  "id": "e2793b9d-518c-4b5e-9103-af8879c421a8"
}
October 7, 2021 9:21 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988435275579",
  "subject": "2988435275579",
  "time": "2021-10-07T13:21:09.2281407Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988435275579",
    "sourceDateTimeUtc": "2021-10-07T13:20:47+00:00",
    "stockNumber": "21011985",
    "reservationId": "38cd40eb-f80d-4849-9579-1ef58045dfe2",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "a12c5281-1249-4b8b-89ae-89466fa5813c"
      },
      {
        "type": "crmId",
        "value": "0016R000036OXTvQAO"
      },
      {
        "type": "ciamId",
        "value": "360E7671-68E2-46C0-8993-3B92CA8FE9E9"
      },
      {
        "type": "storeCustomerId",
        "value": "182148",
        "meta": {
          "key": "locationId",
          "value": "7191"
        }
      }
    ]
  },
  "id": "0d40b100-71d2-4e7f-86c8-f198d905735e"
}
October 7, 2021 9:20 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773767122771",
  "subject": "3773767122771",
  "time": "2021-10-07T13:20:35.2459484Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773767122771",
    "sourceDateTimeUtc": "2021-10-07T13:20:07+00:00",
    "stockNumber": "18939189",
    "reservationId": "faa03d90-e0e6-4eac-9af4-928a837075d9",
    "identity": [
      {
        "type": "ciamId",
        "value": "E617B39F-324F-422A-BC97-542CA1D56082"
      },
      {
        "type": "storeCustomerId",
        "value": "1215361",
        "meta": {
          "key": "locationId",
          "value": "7118"
        }
      },
      {
        "type": "crmId",
        "value": "0016R0000361gFgQAI"
      }
    ]
  },
  "id": "7623fd0f-5d2c-46c4-a8e7-836166c32ef0"
}
October 7, 2021 9:20 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748023410499",
  "subject": "1748023410499",
  "time": "2021-10-07T13:20:35.255663Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748023410499",
    "sourceDateTimeUtc": "2021-10-07T13:20:10+00:00",
    "stockNumber": "20959882",
    "reservationId": "2c73a140-371b-4047-a5ae-7fc725eaf2ad",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00002VIeQIQA1"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~HhCRRx8"
      },
      {
        "type": "storeCustomerId",
        "value": "598944",
        "meta": {
          "key": "locationId",
          "value": "7115"
        }
      },
      {
        "type": "ciamId",
        "value": "45EDF3F7-E9D9-490C-ADDE-B419C7887C2A"
      }
    ]
  },
  "id": "0acaa87d-6302-48f9-b76f-1a9053fa5d85"
}
October 7, 2021 9:20 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988433571643",
  "subject": "2988433571643",
  "time": "2021-10-07T13:20:21.1732254Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988433571643",
    "sourceDateTimeUtc": "2021-10-07T13:19:56+00:00",
    "stockNumber": "21276611",
    "reservationId": "3527788e-dec8-4453-a5bd-bb3ae6ef1939",
    "identity": [
      {
        "type": "cafCustomerId",
        "value": "0012965965"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~UZvhnMZ"
      },
      {
        "type": "ciamId",
        "value": "91BBD7C3-A434-4B00-9B3A-780A95D85662"
      },
      {
        "type": "storeCustomerId",
        "value": "400544",
        "meta": {
          "key": "locationId",
          "value": "7185"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObdsQAC"
      }
    ]
  },
  "id": "598c8a7f-4f18-4c25-b59b-3f0290a3e7f0"
}
October 7, 2021 9:19 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593834815286",
  "subject": "1593834815286",
  "time": "2021-10-07T13:19:48.8763365Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593834815286",
    "sourceDateTimeUtc": "2021-10-07T13:19:32+00:00",
    "stockNumber": "21023259",
    "reservationId": "79db28e0-080a-4395-a83d-682fd3e4535e",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "658298",
        "meta": {
          "key": "locationId",
          "value": "7126"
        }
      },
      {
        "type": "ciamId",
        "value": "BE835790-B900-4B12-9658-EC9794525628"
      }
    ]
  },
  "id": "312c0541-ec76-4a5a-bbf3-472961490b69"
}
October 7, 2021 9:19 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390377652047",
  "subject": "4390377652047",
  "time": "2021-10-07T13:19:47.0365974Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390377652047",
    "sourceDateTimeUtc": "2021-10-07T13:19:19+00:00",
    "stockNumber": "21398397",
    "reservationId": "5523adbc-9f9b-4787-91ed-59d3034a1b79",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "803690",
        "meta": {
          "key": "locationId",
          "value": "7110"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "d2ec888d-9a2d-4d31-bbdd-bd957aef8166"
      },
      {
        "type": "cafCustomerId",
        "value": "0014116441"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~9cAQr0I"
      },
      {
        "type": "ciamId",
        "value": "37988700-7F04-4911-9D64-1CC1CD1448A3"
      },
      {
        "type": "crmId",
        "value": "0011C000033qK1SQAU"
      }
    ]
  },
  "id": "e1d54a52-12a3-48e1-b9df-799f0c55b6d1"
}
October 7, 2021 9:18 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096567500602",
  "subject": "2096567500602",
  "time": "2021-10-07T13:18:35.7077097Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096567500602",
    "sourceDateTimeUtc": "2021-10-07T13:18:10+00:00",
    "stockNumber": "20919145",
    "reservationId": "1d8f86bd-d941-44b6-9d19-e49ff9a90856",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C00001zwsI1QAI"
      },
      {
        "type": "storeCustomerId",
        "value": "400542",
        "meta": {
          "key": "locationId",
          "value": "7185"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "b9ce7a98-9ad4-4b23-ab9f-c244f7456d4d"
      },
      {
        "type": "ciamId",
        "value": "B297B5B9-467F-46AE-9584-4508004DBD5C"
      }
    ]
  },
  "id": "f71935eb-5832-478b-9731-3c9bd5378ff4"
}
October 7, 2021 9:16 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593826328374",
  "subject": "1593826328374",
  "time": "2021-10-07T13:16:15.2808926Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593826328374",
    "sourceDateTimeUtc": "2021-10-07T13:15:52+00:00",
    "stockNumber": "20848548",
    "reservationId": "5605d093-685b-4308-a53f-ded92359aadd",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "6afb7daa-589d-4931-90cf-2c9864c809d9"
      },
      {
        "type": "storeCustomerId",
        "value": "50901",
        "meta": {
          "key": "locationId",
          "value": "7193"
        }
      },
      {
        "type": "ciamId",
        "value": "B69B9222-106F-49A4-B436-F03A8D81945E"
      },
      {
        "type": "crmId",
        "value": "0011C000032Ole9QAC"
      }
    ]
  },
  "id": "926060d0-538e-4292-8ede-4a44f6f565b4"
}
October 7, 2021 9:14 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748009090883",
  "subject": "1748009090883",
  "time": "2021-10-07T13:14:00.4742203Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748009090883",
    "sourceDateTimeUtc": "2021-10-07T13:13:43+00:00",
    "stockNumber": "20885225",
    "reservationId": "7676dcc6-71ac-41c4-8265-794e8715a3b7",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "152363",
        "meta": {
          "key": "locationId",
          "value": "6068"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "a505104c-5959-43b1-8d75-3ce1c1a2224d"
      },
      {
        "type": "ciamId",
        "value": "C8B4EC4C-10FB-433F-8E54-5E1EE7D485F6"
      },
      {
        "type": "crmId",
        "value": "0016R000036O6CSQA0"
      }
    ]
  },
  "id": "0554cd9a-738e-4566-bf54-569195747fed"
}
October 7, 2021 9:14 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593820692278",
  "subject": "1593820692278",
  "time": "2021-10-07T13:14:00.0565081Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593820692278",
    "sourceDateTimeUtc": "2021-10-07T13:13:41+00:00",
    "stockNumber": "21308011",
    "reservationId": "1fcdec70-59dd-49e4-9844-27d227e45fbd",
    "identity": [
      {
        "type": "ciamId",
        "value": "7E11D7A6-D3D0-4274-9C95-050E1A9C23FE"
      },
      {
        "type": "storeCustomerId",
        "value": "952398",
        "meta": {
          "key": "locationId",
          "value": "7111"
        }
      }
    ]
  },
  "id": "c7b240e1-4127-4b68-bebb-fc34bd7a62aa"
}
October 7, 2021 9:13 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352279797576",
  "subject": "2352279797576",
  "time": "2021-10-07T13:13:57.7521613Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352279797576",
    "sourceDateTimeUtc": "2021-10-07T13:13:52+00:00",
    "stockNumber": "20930408",
    "reservationId": "1acdbf4a-54b5-46c8-ba49-a41a512cc90a",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "53840",
        "meta": {
          "key": "locationId",
          "value": "6039"
        }
      },
      {
        "type": "ciamId",
        "value": "983BF5AA-1F49-4B82-AEF4-E735AF651CCF"
      }
    ]
  },
  "id": "51e0b8c6-05ca-4333-b2d9-c75c55a66f22"
}
October 7, 2021 9:13 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096557555514",
  "subject": "2096557555514",
  "time": "2021-10-07T13:13:45.265973Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096557555514",
    "sourceDateTimeUtc": "2021-10-07T13:13:30+00:00",
    "stockNumber": "21223678",
    "reservationId": "b7a78f4a-5c66-460b-9533-dd27fe768c76",
    "identity": [
      {
        "type": "ciamId",
        "value": "665CFAF7-30A0-4E5F-8210-26E7DE55641A"
      },
      {
        "type": "crmId",
        "value": "0016R000036NTPmQAO"
      },
      {
        "type": "buysCustomerId",
        "value": "7b501182-3a45-4063-be97-ff6fc0e2177f"
      },
      {
        "type": "storeCustomerId",
        "value": "171635",
        "meta": {
          "key": "locationId",
          "value": "6024"
        }
      }
    ]
  },
  "id": "147a71e5-f3e7-459c-a3dc-ec534c2b05e4"
}
October 7, 2021 9:12 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988415352635",
  "subject": "2988415352635",
  "time": "2021-10-07T13:12:53.7508988Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988415352635",
    "sourceDateTimeUtc": "2021-10-07T13:12:26+00:00",
    "stockNumber": "21007027",
    "reservationId": "02e6fd91-3307-4c0f-9704-68851032df17",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "223468",
        "meta": {
          "key": "locationId",
          "value": "7274"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "ddd028df-7c75-4c5f-bcba-10e88c9d03cb"
      },
      {
        "type": "crmId",
        "value": "0011C000031aaeOQAQ"
      },
      {
        "type": "ciamId",
        "value": "03ADE0B1-68C7-44C1-89D1-D9ECA7432137"
      }
    ]
  },
  "id": "da68037e-87b7-4368-ae82-a07051919233"
}
October 7, 2021 9:11 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390360661839",
  "subject": "4390360661839",
  "time": "2021-10-07T13:11:50.1127642Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390360661839",
    "sourceDateTimeUtc": "2021-10-07T13:11:33+00:00",
    "stockNumber": "21005091",
    "reservationId": "3a2ed5f6-648f-410e-ac0d-89dab016ad1e",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "435744",
        "meta": {
          "key": "locationId",
          "value": "7173"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002MassXQAR"
      },
      {
        "type": "ciamId",
        "value": "86D27E5F-C883-43D4-8D31-FFA29CED147C"
      }
    ]
  },
  "id": "76325c1a-6fbd-43c5-902f-b88eba17c5cd"
}
October 7, 2021 9:11 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988413861691",
  "subject": "2988413861691",
  "time": "2021-10-07T13:11:05.9724374Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988413861691",
    "sourceDateTimeUtc": "2021-10-07T13:10:53+00:00",
    "stockNumber": "20705730",
    "reservationId": "263ade33-935e-462b-be0a-bffa9317859c",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "11742",
        "meta": {
          "key": "locationId",
          "value": "6142"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002cqtkAQAQ"
      },
      {
        "type": "buysCustomerId",
        "value": "ae929b77-0b86-482f-90f4-234aa7d4eb87"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~12AOFGhh"
      },
      {
        "type": "ciamId",
        "value": "A138BEE0-177D-4BB0-AA7A-2CCF777AA10D"
      }
    ]
  },
  "id": "6455efc5-1c5c-4dfe-aa95-795f462d7e64"
}
October 7, 2021 9:10 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748003897155",
  "subject": "1748003897155",
  "time": "2021-10-07T13:10:35.9698979Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748003897155",
    "sourceDateTimeUtc": "2021-10-07T13:10:25+00:00",
    "stockNumber": "21047898",
    "reservationId": "4c697e8e-15c7-449e-ada8-3c0c48e46333",
    "identity": [
      {
        "type": "ciamId",
        "value": "1AB1547E-A9C3-4B61-A4AF-290BEAC0E4C0"
      },
      {
        "type": "storeCustomerId",
        "value": "33119",
        "meta": {
          "key": "locationId",
          "value": "6086"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036OGNQQA4"
      }
    ]
  },
  "id": "70fc44e6-ca7a-4022-bf69-32e3b341f818"
}
October 7, 2021 9:10 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352274767688",
  "subject": "2352274767688",
  "time": "2021-10-07T13:10:31.0936961Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352274767688",
    "sourceDateTimeUtc": "2021-10-07T13:10:01+00:00",
    "stockNumber": "20835967",
    "reservationId": "708cef1c-a131-422d-bdff-e2dd3ee917ae",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "810149",
        "meta": {
          "key": "locationId",
          "value": "7106"
        }
      },
      {
        "type": "ciamId",
        "value": "56F1935B-46CF-4CAF-B32A-03881461A22C"
      }
    ]
  },
  "id": "df68b266-3a54-4a68-b8ad-35df6b691859"
}
October 7, 2021 9:10 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516267007807",
  "subject": "2516267007807",
  "time": "2021-10-07T13:10:13.899453Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516267007807",
    "sourceDateTimeUtc": "2021-10-07T13:10:05+00:00",
    "stockNumber": "20829468",
    "reservationId": "4d78d3b4-704c-43f9-ba12-45a654184d17",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C000030rkfhQAA"
      },
      {
        "type": "ciamId",
        "value": "F788562F-788E-491D-A0A5-F02EF07AF781"
      },
      {
        "type": "buysCustomerId",
        "value": "ac3aa342-5ffa-432b-85ad-bd657d967df8"
      },
      {
        "type": "storeCustomerId",
        "value": "53553",
        "meta": {
          "key": "locationId",
          "value": "6051"
        }
      }
    ]
  },
  "id": "ed4c89f0-f143-474b-aa57-0917e105887e"
}
October 7, 2021 9:10 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773747281747",
  "subject": "3773747281747",
  "time": "2021-10-07T13:10:00.1311606Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773747281747",
    "sourceDateTimeUtc": "2021-10-07T13:09:36+00:00",
    "stockNumber": "21118966",
    "reservationId": "4121c235-c6bc-44c8-94c0-6b1f971e394d",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036ObTJQA0"
      },
      {
        "type": "buysCustomerId",
        "value": "9b77d3ba-d4d4-4fec-8e98-507ea9412a0f"
      },
      {
        "type": "ciamId",
        "value": "94EC1835-E4C1-4785-B39A-627459D9134E"
      },
      {
        "type": "storeCustomerId",
        "value": "400539",
        "meta": {
          "key": "locationId",
          "value": "7185"
        }
      }
    ]
  },
  "id": "353e71df-bfb3-4319-9e1e-2267f2405a9c"
}
October 7, 2021 9:09 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593816350518",
  "subject": "1593816350518",
  "time": "2021-10-07T13:09:54.9783829Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593816350518",
    "sourceDateTimeUtc": "2021-10-07T13:09:50+00:00",
    "stockNumber": "21303564",
    "reservationId": "0c860c71-2e28-4bf9-a9c4-c0d82812092a",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "120134",
        "meta": {
          "key": "locationId",
          "value": "7233"
        }
      },
      {
        "type": "ciamId",
        "value": "1B15C048-6BEA-425E-8A4C-AAB9960A9E05"
      }
    ]
  },
  "id": "398ba615-d59f-4220-bcab-93eca141ef1c"
}
October 7, 2021 9:08 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516266221375",
  "subject": "2516266221375",
  "time": "2021-10-07T13:08:33.7912009Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516266221375",
    "sourceDateTimeUtc": "2021-10-07T13:07:49+00:00",
    "stockNumber": "20910299",
    "reservationId": "d044fec6-f5db-42cf-bfa8-79572de7d789",
    "identity": [
      {
        "type": "ciamId",
        "value": "A8452C71-9371-43D6-AEDB-F5F9532912CC"
      },
      {
        "type": "storeCustomerId",
        "value": "77717",
        "meta": {
          "key": "locationId",
          "value": "6013"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObVyQAK"
      }
    ]
  },
  "id": "ac7309b7-df34-47e9-b826-3ef422932a92"
}
October 7, 2021 9:08 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390359252815",
  "subject": "4390359252815",
  "time": "2021-10-07T13:08:25.2472445Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390359252815",
    "sourceDateTimeUtc": "2021-10-07T13:08:01+00:00",
    "stockNumber": "21325556",
    "reservationId": "6fc120c0-a35e-482d-98f4-4ac2d6c1c1ac",
    "identity": [
      {
        "type": "ciamId",
        "value": "AD91F55B-01A8-4DD9-899D-9C6D1F5C0E3D"
      },
      {
        "type": "crmId",
        "value": "0016R0000361sgGQAQ"
      },
      {
        "type": "storeCustomerId",
        "value": "810148",
        "meta": {
          "key": "locationId",
          "value": "7106"
        }
      }
    ]
  },
  "id": "9681ea2f-816d-4bba-b7fb-f01c96882c72"
}
October 7, 2021 9:08 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748003159875",
  "subject": "1748003159875",
  "time": "2021-10-07T13:08:24.5145599Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748003159875",
    "sourceDateTimeUtc": "2021-10-07T13:08:06+00:00",
    "stockNumber": "21077803",
    "reservationId": "cb61fe64-56f7-49ca-9960-a31515f0c0d1",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "551233",
        "meta": {
          "key": "locationId",
          "value": "7154"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "5c34f51b-9a6a-4071-8056-1575827deedc"
      },
      {
        "type": "crmId",
        "value": "0011C00002vMHldQAG"
      },
      {
        "type": "ciamId",
        "value": "50F4C914-EF72-489A-8058-FD593745A426"
      }
    ]
  },
  "id": "a2e9b210-af4f-43d3-b7a2-2dfb9bbe61cb"
}
October 7, 2021 9:07 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593815514934",
  "subject": "1593815514934",
  "time": "2021-10-07T13:07:47.1427829Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593815514934",
    "sourceDateTimeUtc": "2021-10-07T13:07:21+00:00",
    "stockNumber": "21180186",
    "reservationId": "057d9660-268a-4dc0-bf09-9bc1eeb346b9",
    "identity": [
      {
        "type": "crmId",
        "value": "0011500001huuaQAAQ"
      },
      {
        "type": "storeCustomerId",
        "value": "898346",
        "meta": {
          "key": "locationId",
          "value": "7102"
        }
      },
      {
        "type": "ciamId",
        "value": "9A15B0BF-339C-49F0-B80B-D777881EA740"
      }
    ]
  },
  "id": "9a460ef9-a07e-488a-b0ae-1c786b819595"
}
October 7, 2021 9:07 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352272850760",
  "subject": "2352272850760",
  "time": "2021-10-07T13:07:11.3210681Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352272850760",
    "sourceDateTimeUtc": "2021-10-07T13:06:39+00:00",
    "stockNumber": "20828262",
    "reservationId": "a99bf2be-856d-4106-8100-d75bb09c90c2",
    "identity": [
      {
        "type": "crmId",
        "value": "0011C000026rxnkQAA"
      },
      {
        "type": "buysCustomerId",
        "value": "d651c489-0ed2-4e66-b672-d740d1f66316"
      },
      {
        "type": "ciamId",
        "value": "B7C76E4A-0A87-4373-9AEC-A30C00F7428E"
      },
      {
        "type": "storeCustomerId",
        "value": "324063",
        "meta": {
          "key": "locationId",
          "value": "7279"
        }
      }
    ]
  },
  "id": "e414cfdd-0d3b-4149-b44d-fbb9a647583f"
}
October 7, 2021 9:05 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1748001570627",
  "subject": "1748001570627",
  "time": "2021-10-07T13:05:45.3145495Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1748001570627",
    "sourceDateTimeUtc": "2021-10-07T13:05:37+00:00",
    "stockNumber": "21219837",
    "reservationId": "336041f3-d4dd-48fc-8272-27b9333542dd",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "28266",
        "meta": {
          "key": "locationId",
          "value": "6134"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "378b4a9a-8c86-4f67-ba01-006492eb02f3"
      },
      {
        "type": "crmId",
        "value": "0011C00002v0sI8QAI"
      },
      {
        "type": "ciamId",
        "value": "DFFC2975-430F-426C-BBED-29EE91CAD333"
      }
    ]
  },
  "id": "7bac8d84-6a03-4a9d-bd91-582204b23b99"
}
October 7, 2021 9:04 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390358122319",
  "subject": "4390358122319",
  "time": "2021-10-07T13:04:56.3741136Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390358122319",
    "sourceDateTimeUtc": "2021-10-07T13:04:23+00:00",
    "stockNumber": "21230490",
    "reservationId": "c0dc5704-63af-4f9e-b438-bbb08810b770",
    "identity": [
      {
        "type": "ciamId",
        "value": "B7B356BF-C132-4C62-9EF0-700E2649520E"
      },
      {
        "type": "storeCustomerId",
        "value": "32568",
        "meta": {
          "key": "locationId",
          "value": "6047"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "ffa43504-58dd-43fc-8140-a6b10a5fb3da"
      },
      {
        "type": "crmId",
        "value": "0011C00002ctia2QAA"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~DIW4Igb"
      },
      {
        "type": "cafCustomerId",
        "value": "0013910420"
      }
    ]
  },
  "id": "e01f4b35-bb10-4472-8d5e-225e06f7dbb3"
}
October 7, 2021 9:03 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516264075071",
  "subject": "2516264075071",
  "time": "2021-10-07T13:03:32.7333968Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516264075071",
    "sourceDateTimeUtc": "2021-10-07T13:03:07+00:00",
    "stockNumber": "21109793",
    "reservationId": "65cec9fd-485d-4e37-aff3-f55054cc4925",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "52755",
        "meta": {
          "key": "locationId",
          "value": "6054"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "34ebf2fc-4f7b-49ba-96d1-dfc9791b7816"
      },
      {
        "type": "crmId",
        "value": "0016R0000360bSwQAI"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~KZV3KEz"
      },
      {
        "type": "ciamId",
        "value": "592FFF0E-90C8-47F7-82AF-CCFEDB2F3333"
      }
    ]
  },
  "id": "c8ddbebb-1db9-4c95-bfd4-dcc9db5aeb29"
}
October 7, 2021 9:03 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352271195976",
  "subject": "2352271195976",
  "time": "2021-10-07T13:03:21.2742205Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352271195976",
    "sourceDateTimeUtc": "2021-10-07T13:03:03+00:00",
    "stockNumber": "21166777",
    "reservationId": "7b3f5555-091e-4bf5-a04f-027ec1d6c5be",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "737601",
        "meta": {
          "key": "locationId",
          "value": "7121"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObTTQA0"
      },
      {
        "type": "ciamId",
        "value": "09A7B1C9-CDAF-4552-B628-AC694FDE658D"
      }
    ]
  },
  "id": "48eb0b6c-0b39-4b53-9208-8eac3d41e0b3"
}
October 7, 2021 9:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352270311240",
  "subject": "2352270311240",
  "time": "2021-10-07T13:01:41.7644539Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352270311240",
    "sourceDateTimeUtc": "2021-10-07T13:01:13+00:00",
    "stockNumber": "21194476",
    "reservationId": "29a26f6b-2893-4c21-b428-e9d2ae76259a",
    "identity": [
      {
        "type": "cafCustomerId",
        "value": "0010336612"
      },
      {
        "type": "ciamId",
        "value": "9A029A09-F9FA-44E8-BD83-A347016272F2"
      },
      {
        "type": "storeCustomerId",
        "value": "952396",
        "meta": {
          "key": "locationId",
          "value": "7111"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036NKUiQAO"
      },
      {
        "type": "buysCustomerId",
        "value": "e955458c-9791-41a5-8aa9-80f7d6710022"
      }
    ]
  },
  "id": "b3d22c69-2016-4bdc-a585-a55bcfaa6634"
}
October 7, 2021 9:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988409110331",
  "subject": "2988409110331",
  "time": "2021-10-07T13:01:41.7553361Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988409110331",
    "sourceDateTimeUtc": "2021-10-07T13:01:21+00:00",
    "stockNumber": "21325892",
    "reservationId": "ea0661fb-c309-4d6b-8222-87d475fcdcfd",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "e29da24d-b014-4613-85fe-4f1d1f7d738a"
      },
      {
        "type": "storeCustomerId",
        "value": "1290669",
        "meta": {
          "key": "locationId",
          "value": "7104"
        }
      },
      {
        "type": "ciamId",
        "value": "0D5874C2-65C5-45B0-A243-0CC0FE1B95E8"
      },
      {
        "type": "crmId",
        "value": "0011C00002mFBdLQAW"
      }
    ]
  },
  "id": "94d62537-5484-4b21-96fa-d2859bd18bc0"
}
October 7, 2021 8:59 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812404326209",
  "subject": "812404326209",
  "time": "2021-10-07T12:59:51.280877Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812404326209",
    "sourceDateTimeUtc": "2021-10-07T00:59:41+00:00",
    "stockNumber": "20243577",
    "reservationId": "36ae8273-212d-44d3-9c83-dea4f244e02d",
    "identity": [
      {
        "type": "ciamId",
        "value": "F0136103-A566-4B0F-9E21-F42A87BA5221"
      },
      {
        "type": "storeCustomerId",
        "value": "45580",
        "meta": {
          "key": "locationId",
          "value": "6070"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "d8959ddd-262f-4da6-90d7-7c6345368e72"
      },
      {
        "type": "crmId",
        "value": "0011C00002wa7JTQAY"
      }
    ]
  },
  "id": "b72acb49-ec42-4d74-9611-808797e9f556"
}
October 7, 2021 8:59 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593811631926",
  "subject": "1593811631926",
  "time": "2021-10-07T12:59:06.1153082Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593811631926",
    "sourceDateTimeUtc": "2021-10-07T00:58:33+00:00",
    "stockNumber": "21180548",
    "reservationId": "356d1820-1d55-4b67-9491-68edcfb8e3cf",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "45579",
        "meta": {
          "key": "locationId",
          "value": "6070"
        }
      },
      {
        "type": "ciamId",
        "value": "C9363A27-4282-47CF-8212-0FDA6BFF2BB6"
      },
      {
        "type": "crmId",
        "value": "0016R000036OCocQAG"
      },
      {
        "type": "buysCustomerId",
        "value": "92070ddb-87f6-4fa1-ad40-3028bed19395"
      }
    ]
  },
  "id": "785efc93-1170-4c9b-ac15-57200f80b203"
}
October 7, 2021 8:58 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988407815995",
  "subject": "2988407815995",
  "time": "2021-10-07T12:58:19.1686626Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988407815995",
    "sourceDateTimeUtc": "2021-10-07T00:57:45+00:00",
    "stockNumber": "21010800",
    "reservationId": "32be5e9a-4874-41e4-91eb-81262eda5727",
    "identity": [
      {
        "type": "ciamId",
        "value": "12EA78C2-2A8D-45DE-AD1F-B55A18D92BCE"
      },
      {
        "type": "crmId",
        "value": "0016R000036NmzaQAC"
      },
      {
        "type": "storeCustomerId",
        "value": "737203",
        "meta": {
          "key": "locationId",
          "value": "7121"
        }
      }
    ]
  },
  "id": "840c471a-5df2-424a-8464-561c6abd2eaa"
}
October 7, 2021 8:55 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593810435894",
  "subject": "1593810435894",
  "time": "2021-10-07T12:55:06.4918014Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593810435894",
    "sourceDateTimeUtc": "2021-10-07T00:54:46+00:00",
    "stockNumber": "21079073",
    "reservationId": "ea86dc80-505a-4cb3-bea9-cee761a5115d",
    "identity": [
      {
        "type": "ciamId",
        "value": "A607DCC9-BF4D-4CF2-8123-28DFDF9266A8"
      },
      {
        "type": "storeCustomerId",
        "value": "255020",
        "meta": {
          "key": "locationId",
          "value": "7654"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "2885970b-a5af-4cc0-a93d-5e6e7761fe96"
      },
      {
        "type": "crmId",
        "value": "0016R000036OQckQAG"
      }
    ]
  },
  "id": "45cdc140-ea5a-4169-9a81-af1bcc640273"
}
October 7, 2021 8:53 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096547479354",
  "subject": "2096547479354",
  "time": "2021-10-07T12:53:54.2384508Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096547479354",
    "sourceDateTimeUtc": "2021-10-07T00:52:53+00:00",
    "stockNumber": "21110108",
    "reservationId": "309462f1-50c1-402a-b3b0-b3e5d146bc43",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "150828",
        "meta": {
          "key": "locationId",
          "value": "7186"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObP2QAK"
      },
      {
        "type": "ciamId",
        "value": "F8743E9F-E6DE-4CE1-8836-331AB4627B71"
      }
    ]
  },
  "id": "31c9d1de-852b-4129-8b62-36165769daa2"
}
October 7, 2021 8:53 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096547512122",
  "subject": "2096547512122",
  "time": "2021-10-07T12:53:31.6364976Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096547512122",
    "sourceDateTimeUtc": "2021-10-07T00:53:13+00:00",
    "stockNumber": "20641192",
    "reservationId": "030443b1-3393-48e9-9ce5-58ed498b8afd",
    "identity": [
      {
        "type": "ciamId",
        "value": "498B8F35-E69B-4C7C-BF70-9B11376A78DC"
      },
      {
        "type": "storeCustomerId",
        "value": "810147",
        "meta": {
          "key": "locationId",
          "value": "7106"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002JSNBcQAP"
      },
      {
        "type": "cafCustomerId",
        "value": "0012908938"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~WiKSCIZ"
      },
      {
        "type": "buysCustomerId",
        "value": "daedaca5-1b7e-4401-b9e5-cc6a567a5917"
      }
    ]
  },
  "id": "5f68a6fb-50b2-48af-bfb0-d00ab3dc9eb5"
}
October 7, 2021 8:49 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096545939258",
  "subject": "2096545939258",
  "time": "2021-10-07T12:49:32.083413Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096545939258",
    "sourceDateTimeUtc": "2021-10-07T00:49:08+00:00",
    "stockNumber": "20623536",
    "reservationId": "3ee3efdf-527a-40d1-8046-a279669a6acf",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "a089fc3c-b6cf-46f5-8013-94bd6c9dc7a5"
      },
      {
        "type": "crmId",
        "value": "0016R000036LlApQAK"
      },
      {
        "type": "ciamId",
        "value": "56514F0B-789A-4AB4-B0A2-53F8C2DC9A42"
      },
      {
        "type": "storeCustomerId",
        "value": "53836",
        "meta": {
          "key": "locationId",
          "value": "6039"
        }
      }
    ]
  },
  "id": "31970364-c5a8-418d-84c0-6da8969c3e00"
}
October 7, 2021 8:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773737484115",
  "subject": "3773737484115",
  "time": "2021-10-07T12:47:04.7049053Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773737484115",
    "sourceDateTimeUtc": "2021-10-07T00:46:24+00:00",
    "stockNumber": "20708487",
    "reservationId": "90aa015b-d155-477d-8b00-b37c3565f8a1",
    "identity": [
      {
        "type": "cafCustomerId",
        "value": "0013313432"
      },
      {
        "type": "ciamId",
        "value": "36A01BCC-1E49-46DA-8CF6-AB2D0188605C"
      },
      {
        "type": "buysCustomerId",
        "value": "3a80c6cc-29ec-4096-8e48-a698df7ffce4"
      },
      {
        "type": "storeCustomerId",
        "value": "44824",
        "meta": {
          "key": "locationId",
          "value": "6020"
        }
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~GyxdwqC"
      },
      {
        "type": "crmId",
        "value": "0011C00002eawPWQAY"
      }
    ]
  },
  "id": "47255582-3d2a-4f76-af8b-505a62ac5519"
}
October 7, 2021 8:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390350683983",
  "subject": "4390350683983",
  "time": "2021-10-07T12:47:01.5980909Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390350683983",
    "sourceDateTimeUtc": "2021-10-07T00:44:50+00:00",
    "stockNumber": "21152932",
    "reservationId": "d3b0a6cf-3e74-4ec2-a5de-c515b1e510cf",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "1212151",
        "meta": {
          "key": "locationId",
          "value": "7118"
        }
      },
      {
        "type": "crmId",
        "value": "0016R0000362YrWQAU"
      },
      {
        "type": "ciamId",
        "value": "13C7447E-5541-42C2-8C4A-F6899CA6183F"
      }
    ]
  },
  "id": "a083733b-20ed-485e-8e97-69bb2985c154"
}
October 7, 2021 8:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096540745530",
  "subject": "2096540745530",
  "time": "2021-10-07T12:47:00.7288474Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096540745530",
    "sourceDateTimeUtc": "2021-10-07T00:36:57+00:00",
    "stockNumber": "20774482",
    "reservationId": "77104827-51bd-4d88-b6b9-a84816a06f72",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "68652",
        "meta": {
          "key": "locationId",
          "value": "6067"
        }
      },
      {
        "type": "ciamId",
        "value": "32B7F178-9CEB-4150-9D20-9C7AEE28F2E9"
      },
      {
        "type": "buysCustomerId",
        "value": "c693824b-5b8b-4880-8ea9-2342cca5fb4d"
      },
      {
        "type": "crmId",
        "value": "0016R000036ObHIQA0"
      }
    ]
  },
  "id": "88adc01d-8f44-4d7d-b4ba-36d65a8b3401"
}
October 7, 2021 8:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096543121210",
  "subject": "2096543121210",
  "time": "2021-10-07T12:46:59.6395548Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096543121210",
    "sourceDateTimeUtc": "2021-10-07T00:44:34+00:00",
    "stockNumber": "20449781",
    "reservationId": "f703a9c6-840f-42dc-8722-64b4d35d35c6",
    "identity": [
      {
        "type": "ciamId",
        "value": "B95C037F-66DC-4893-AC1B-17F089C3563A"
      },
      {
        "type": "storeCustomerId",
        "value": "135475",
        "meta": {
          "key": "locationId",
          "value": "6001"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObHhQAK"
      },
      {
        "type": "buysCustomerId",
        "value": "2f9bca6a-d7b5-4bee-a580-d783c47ed9bf"
      }
    ]
  },
  "id": "55068a9f-4470-4777-8d53-45a78bc83151"
}
October 7, 2021 8:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773736042323",
  "subject": "3773736042323",
  "time": "2021-10-07T12:46:34.5631953Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773736042323",
    "sourceDateTimeUtc": "2021-10-07T00:41:53+00:00",
    "stockNumber": "19645441",
    "reservationId": "9a659765-6223-4ac5-bca8-19c65249e02e",
    "identity": [
      {
        "type": "ciamId",
        "value": "9B76C3EF-A658-4F7F-B752-B295CD505205"
      },
      {
        "type": "storeCustomerId",
        "value": "35686",
        "meta": {
          "key": "locationId",
          "value": "6092"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036ObK2QAK"
      },
      {
        "type": "buysCustomerId",
        "value": "cb07d007-7446-468c-a56b-bb9ceb68e326"
      }
    ]
  },
  "id": "00af2365-cf36-4339-a190-1f68133caf65"
}
October 7, 2021 8:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988401671995",
  "subject": "2988401671995",
  "time": "2021-10-07T12:46:18.2279758Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988401671995",
    "sourceDateTimeUtc": "2021-10-07T00:39:08+00:00",
    "stockNumber": "20539589",
    "reservationId": "0437cae5-7457-4844-bd04-c39dd2579d34",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "43030",
        "meta": {
          "key": "locationId",
          "value": "6138"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "ed4392b5-7902-4143-ae1c-bf9a7781a5fc"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~RxVrdDX"
      },
      {
        "type": "crmId",
        "value": "0011C00002OFTxXQAX"
      },
      {
        "type": "ciamId",
        "value": "25D18896-BD35-451C-9310-9F0100BB025E"
      },
      {
        "type": "cafCustomerId",
        "value": "0012867307"
      }
    ]
  },
  "id": "7334bbc9-fe5e-401e-9e75-72393a76f84f"
}
October 7, 2021 8:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988385369915",
  "subject": "2988385369915",
  "time": "2021-10-07T12:46:16.6762009Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988385369915",
    "sourceDateTimeUtc": "2021-10-07T00:28:57+00:00",
    "stockNumber": "21168983",
    "reservationId": "4a534bbc-53c6-4fe0-bcdc-58b5bda08e9c",
    "identity": [
      {
        "type": "ciamId",
        "value": "080598DA-2C7F-4368-A88D-5C7556AFC239"
      },
      {
        "type": "storeCustomerId",
        "value": "115168",
        "meta": {
          "key": "locationId",
          "value": "6025"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "f204e549-8cf5-4603-ade4-161e4cd3046c"
      },
      {
        "type": "crmId",
        "value": "0016R000036ObF3QAK"
      }
    ]
  },
  "id": "a65506f3-6a44-48a9-a845-d77a7064c635"
}
October 7, 2021 8:46 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988392791867",
  "subject": "2988392791867",
  "time": "2021-10-07T12:46:13.5576587Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988392791867",
    "sourceDateTimeUtc": "2021-10-07T00:32:21+00:00",
    "stockNumber": "21405054",
    "reservationId": "b1ef5298-7a6a-462a-b23c-557f4f38b7e5",
    "identity": [
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~7NbkLQA"
      },
      {
        "type": "crmId",
        "value": "0011C00002nYVGFQA4"
      },
      {
        "type": "cafCustomerId",
        "value": "0013960030"
      },
      {
        "type": "buysCustomerId",
        "value": "78d2d92a-e316-43db-b5ec-f7f3a0436164"
      },
      {
        "type": "storeCustomerId",
        "value": "174606",
        "meta": {
          "key": "locationId",
          "value": "7211"
        }
      },
      {
        "type": "ciamId",
        "value": "BA90F618-D70A-4944-B3D2-AC3D016D8E31"
      }
    ]
  },
  "id": "a35f5d17-d22d-4f1a-a4d2-a26a8c8090fb"
}
October 7, 2021 8:33 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593698713398",
  "subject": "1593698713398",
  "time": "2021-10-07T12:33:33.7193353Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593698713398",
    "sourceDateTimeUtc": "2021-10-07T00:25:13+00:00",
    "stockNumber": "21119638",
    "reservationId": "0d64ba8e-01c2-4999-9797-1063287baa98",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036ObEsQAK"
      },
      {
        "type": "ciamId",
        "value": "0092AC38-951C-4F55-B063-14B6864113F0"
      },
      {
        "type": "storeCustomerId",
        "value": "400536",
        "meta": {
          "key": "locationId",
          "value": "7185"
        }
      },
      {
        "type": "buysCustomerId",
        "value": "d287c468-c460-4d71-be8f-62ac7573d9e3"
      }
    ]
  },
  "id": "e65037ca-09d8-4f57-9b6d-5173fb0b60a1"
}
October 7, 2021 8:22 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988235423547",
  "subject": "2988235423547",
  "time": "2021-10-07T12:22:44.1166074Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988235423547",
    "sourceDateTimeUtc": "2021-10-07T00:22:14+00:00",
    "stockNumber": "21285794",
    "reservationId": "933834fb-ad69-4d94-ba50-6b12efbdbf11",
    "identity": [
      {
        "type": "ciamId",
        "value": "8B2DE836-5C6B-47F2-AE7B-AFBE88330624"
      },
      {
        "type": "buysCustomerId",
        "value": "f8e502e0-f4cd-454f-82fe-94fd51dd42de"
      },
      {
        "type": "storeCustomerId",
        "value": "716873",
        "meta": {
          "key": "locationId",
          "value": "7128"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036NqrZQAS"
      }
    ]
  },
  "id": "066975c9-e4b2-45f8-85e3-c0b76c874ab4"
}
October 7, 2021 8:21 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593631014710",
  "subject": "1593631014710",
  "time": "2021-10-07T12:21:00.60112Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593631014710",
    "sourceDateTimeUtc": "2021-10-07T00:20:36+00:00",
    "stockNumber": "21192144",
    "reservationId": "cdd89ff0-4523-4412-97c0-96c350e1aed6",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "297762",
        "meta": {
          "key": "locationId",
          "value": "7283"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000035R5UdQAK"
      },
      {
        "type": "ciamId",
        "value": "DDCE2820-E463-4BE3-872E-919BC3B52107"
      }
    ]
  },
  "id": "5829bea7-faff-4e82-aa05-9ec1633ffe19"
}
October 7, 2021 8:20 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2516082179903",
  "subject": "2516082179903",
  "time": "2021-10-07T12:20:24.9997925Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2516082179903",
    "sourceDateTimeUtc": "2021-10-07T00:20:19+00:00",
    "stockNumber": "20859839",
    "reservationId": "830ed2d6-9952-4522-be95-995942056b10",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "9c0bc76d-ab8d-4ef8-9cfb-7f0ea5f4a325"
      },
      {
        "type": "storeCustomerId",
        "value": "142058",
        "meta": {
          "key": "locationId",
          "value": "7209"
        }
      },
      {
        "type": "ciamId",
        "value": "B2BE9F54-B1EF-4E14-8BBA-3789F1D68350"
      },
      {
        "type": "crmId",
        "value": "0016R000036OWZmQAO"
      }
    ]
  },
  "id": "82b9b5c8-bb73-4346-8ce1-cb0738d2954c"
}
October 7, 2021 8:19 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773566779219",
  "subject": "3773566779219",
  "time": "2021-10-07T12:19:25.4359217Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773566779219",
    "sourceDateTimeUtc": "2021-10-07T00:19:06+00:00",
    "stockNumber": "21078988",
    "reservationId": "7536d39e-c1bf-4474-a468-88aa6b04571b",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "60ab94e3-58c8-4a97-b5ac-b418ef0a526c"
      },
      {
        "type": "storeCustomerId",
        "value": "564593",
        "meta": {
          "key": "locationId",
          "value": "7653"
        }
      },
      {
        "type": "crmId",
        "value": "0016R0000363XeTQAU"
      },
      {
        "type": "ciamId",
        "value": "8300B08D-7F0C-4D7A-9BAC-B344A9570225"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~jYrsnLT"
      }
    ]
  },
  "id": "f403e2f2-c6da-4aa1-a2da-968d20568f78"
}
October 7, 2021 8:18 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352087301960",
  "subject": "2352087301960",
  "time": "2021-10-07T12:18:20.2040134Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352087301960",
    "sourceDateTimeUtc": "2021-10-07T00:17:48+00:00",
    "stockNumber": "20541559",
    "reservationId": "7649e099-071f-48d2-ae61-430f76213812",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "34142",
        "meta": {
          "key": "locationId",
          "value": "6107"
        }
      },
      {
        "type": "ciamId",
        "value": "12A6D6D0-BBD3-4A09-B7BF-EAC80C27A8FF"
      },
      {
        "type": "crmId",
        "value": "0016R000036ODiaQAG"
      }
    ]
  },
  "id": "812980d7-8656-4e0b-b98c-5cfc2584e301"
}
October 7, 2021 8:18 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2988226543419",
  "subject": "2988226543419",
  "time": "2021-10-07T12:18:07.4444413Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2988226543419",
    "sourceDateTimeUtc": "2021-10-07T00:17:34+00:00",
    "stockNumber": "20446407",
    "reservationId": "a6e1f6bc-2bfd-46d7-b33d-aba3e0928870",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "100049",
        "meta": {
          "key": "locationId",
          "value": "6080"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036Ob9PQAS"
      },
      {
        "type": "ciamId",
        "value": "238EAEB6-8FFD-4B03-B071-AE4C0FC3982A"
      }
    ]
  },
  "id": "8ddc8b5a-7d8a-464f-9ff6-6f46c5376a15"
}
October 7, 2021 8:18 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390167904079",
  "subject": "4390167904079",
  "time": "2021-10-07T12:18:02.6527666Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390167904079",
    "sourceDateTimeUtc": "2021-10-07T00:17:52+00:00",
    "stockNumber": "21339867",
    "reservationId": "957c40e7-d066-4ab4-b5b9-207020d8e2a3",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "114421",
        "meta": {
          "key": "locationId",
          "value": "6081"
        }
      },
      {
        "type": "ciamId",
        "value": "44DDE4C6-FA43-400B-936E-A2517FE58E81"
      }
    ]
  },
  "id": "102871f0-bf24-4a16-a93f-05a2adef507a"
}
October 7, 2021 8:15 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/4390162005839",
  "subject": "4390162005839",
  "time": "2021-10-07T12:15:42.6314278Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "4390162005839",
    "sourceDateTimeUtc": "2021-10-07T00:15:29+00:00",
    "stockNumber": "21134581",
    "reservationId": "51187374-f4d9-4f6b-ab1e-9dc6982d0752",
    "identity": [
      {
        "type": "ciamId",
        "value": "5AF20DA1-20DF-4D72-8D61-4FAC32851951"
      },
      {
        "type": "storeCustomerId",
        "value": "34136",
        "meta": {
          "key": "locationId",
          "value": "6007"
        }
      }
    ]
  },
  "id": "6a570675-cc52-4277-b58d-7e3e59a5b5b7"
}
October 7, 2021 8:15 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096368271162",
  "subject": "2096368271162",
  "time": "2021-10-07T12:15:39.3453861Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096368271162",
    "sourceDateTimeUtc": "2021-10-07T00:15:10+00:00",
    "stockNumber": "20382968",
    "reservationId": "373f456a-a4be-4d43-9ef4-9c627b3e86df",
    "identity": [
      {
        "type": "crmId",
        "value": "0016R000036Ob8pQAC"
      },
      {
        "type": "storeCustomerId",
        "value": "11739",
        "meta": {
          "key": "locationId",
          "value": "6142"
        }
      },
      {
        "type": "ciamId",
        "value": "1B323162-31D0-4D04-9408-0133607D55F9"
      }
    ]
  },
  "id": "da314304-8076-49ee-a388-95f0b0a8407c"
}
October 7, 2021 8:14 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096366288698",
  "subject": "2096366288698",
  "time": "2021-10-07T12:14:37.3408658Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096366288698",
    "sourceDateTimeUtc": "2021-10-07T00:14:13+00:00",
    "stockNumber": "20376814",
    "reservationId": "7ff54ecd-afc4-42f3-9ffb-e44b1fab99e6",
    "identity": [
      {
        "type": "ciamId",
        "value": "26FB5910-7494-46CE-AF4B-F8825F5C0F25"
      },
      {
        "type": "storeCustomerId",
        "value": "100048",
        "meta": {
          "key": "locationId",
          "value": "6080"
        }
      }
    ]
  },
  "id": "d3e53a1b-143a-45fc-8a1c-7840ed53b430"
}
October 7, 2021 8:13 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812222857025",
  "subject": "812222857025",
  "time": "2021-10-07T12:13:54.1461512Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812222857025",
    "sourceDateTimeUtc": "2021-10-07T00:13:20+00:00",
    "stockNumber": "21234749",
    "reservationId": "222c00c6-3dea-4dc1-ae21-f723f455aaa2",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "335644",
        "meta": {
          "key": "locationId",
          "value": "7241"
        }
      },
      {
        "type": "ciamId",
        "value": "03D1EC7F-45D4-4851-91A0-1CA23349E04F"
      }
    ]
  },
  "id": "153ed09e-8318-4106-aeba-33778f0f1e80"
}
October 7, 2021 8:11 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096362028858",
  "subject": "2096362028858",
  "time": "2021-10-07T12:11:30.2811513Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096362028858",
    "sourceDateTimeUtc": "2021-10-07T00:11:04+00:00",
    "stockNumber": "21233432",
    "reservationId": "48614510-0fd1-4020-949a-c34772f2ba93",
    "identity": [
      {
        "type": "cafCustomerId",
        "value": "0014372304"
      },
      {
        "type": "storeCustomerId",
        "value": "69440",
        "meta": {
          "key": "locationId",
          "value": "7260"
        }
      },
      {
        "type": "ciamId",
        "value": "938FE6E8-EC15-4160-8CF6-D07DD213B3C3"
      },
      {
        "type": "crmId",
        "value": "0011C00001s9yHlQAI"
      },
      {
        "type": "buysCustomerId",
        "value": "06c2748e-91ee-482e-858c-d0f844a6acd0"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxVechPurFlag~XlbDtQa"
      }
    ]
  },
  "id": "1579ee99-b4af-493b-85ca-26c1859b8300"
}
October 7, 2021 8:08 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812219858753",
  "subject": "812219858753",
  "time": "2021-10-07T12:08:31.3568874Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812219858753",
    "sourceDateTimeUtc": "2021-10-07T00:08:22+00:00",
    "stockNumber": "21234901",
    "reservationId": "644a65ad-2aeb-4b4d-8cc2-1a9d8d790b4a",
    "identity": [
      {
        "type": "cafCustomerId",
        "value": "0012039237"
      },
      {
        "type": "buysCustomerId",
        "value": "260a8471-3ebf-4db4-a97a-4415fce67931"
      },
      {
        "type": "storeCustomerId",
        "value": "335643",
        "meta": {
          "key": "locationId",
          "value": "7241"
        }
      },
      {
        "type": "crmId",
        "value": "0011C00002pOKYgQAO"
      },
      {
        "type": "ciamId",
        "value": "3A870CBF-F364-48C7-940F-6956410CAB3E"
      }
    ]
  },
  "id": "1e4297ff-0799-4273-b4de-9809f46b7295"
}
October 7, 2021 8:07 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/1593610731318",
  "subject": "1593610731318",
  "time": "2021-10-07T12:07:53.2411649Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "1593610731318",
    "sourceDateTimeUtc": "2021-10-07T00:07:39+00:00",
    "stockNumber": "20907504",
    "reservationId": "0ab2c23f-3dcd-41b8-b860-60833dc01f45",
    "identity": [
      {
        "type": "storeCustomerId",
        "value": "732233",
        "meta": {
          "key": "locationId",
          "value": "7112"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036NzNtQAK"
      },
      {
        "type": "cafCustomerId",
        "value": "0010815497"
      },
      {
        "type": "ciamId",
        "value": "AB333AE3-42A1-46D7-B444-A46A00F52A98"
      }
    ]
  },
  "id": "ab0ad985-2d22-4df4-a53b-ae7ac359b3b2"
}
October 7, 2021 8:05 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/3773551689555",
  "subject": "3773551689555",
  "time": "2021-10-07T12:05:39.4928719Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "3773551689555",
    "sourceDateTimeUtc": "2021-10-07T00:05:32+00:00",
    "stockNumber": "21340015",
    "reservationId": "88830a92-7812-4b45-910f-f84674bd7ce4",
    "identity": [
      {
        "type": "buysCustomerId",
        "value": "a4c43398-f8c0-49bc-879f-1ef52f672505"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~HeHJ6IX"
      },
      {
        "type": "storeCustomerId",
        "value": "114420",
        "meta": {
          "key": "locationId",
          "value": "6081"
        }
      },
      {
        "type": "ciamId",
        "value": "8FD86643-9A77-4806-823E-83C21C19DAB0"
      },
      {
        "type": "crmId",
        "value": "0016R0000362hDRQAY"
      }
    ]
  },
  "id": "b81028e5-d3fd-42aa-94fb-ea365e634912"
}
October 7, 2021 8:04 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2096360963898",
  "subject": "2096360963898",
  "time": "2021-10-07T12:04:24.9258079Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2096360963898",
    "sourceDateTimeUtc": "2021-10-07T00:03:51+00:00",
    "stockNumber": "20798389",
    "reservationId": "eef7cf51-c715-4c72-b5a9-ad3dc0ea9023",
    "identity": [
      {
        "type": "ciamId",
        "value": "A6F19F43-2431-42D2-94C1-87C4FDC8387D"
      },
      {
        "type": "storeCustomerId",
        "value": "333205",
        "meta": {
          "key": "locationId",
          "value": "7243"
        }
      }
    ]
  },
  "id": "3a20b350-e46a-4e89-a96d-6e1a69605fb7"
}
October 7, 2021 8:03 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812218990401",
  "subject": "812218990401",
  "time": "2021-10-07T12:03:57.7946847Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812218990401",
    "sourceDateTimeUtc": "2021-10-07T00:03:21+00:00",
    "stockNumber": "21385283",
    "reservationId": "628a1dee-6aab-4c11-aed6-df73c20d102b",
    "identity": [
      {
        "type": "ciamId",
        "value": "5958B331-25F7-4868-B25C-D53816228E56"
      },
      {
        "type": "storeCustomerId",
        "value": "1027933",
        "meta": {
          "key": "locationId",
          "value": "7132"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036Ob8QQAS"
      }
    ]
  },
  "id": "cceec7af-592e-4d99-b174-9025be4d3aaf"
}
October 7, 2021 8:02 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352072294216",
  "subject": "2352072294216",
  "time": "2021-10-07T12:02:49.7676785Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352072294216",
    "sourceDateTimeUtc": "2021-10-07T00:02:39+00:00",
    "stockNumber": "21110174",
    "reservationId": "b773a489-6877-4264-84a4-dca76970b244",
    "identity": [
      {
        "type": "ciamId",
        "value": "3B967D32-8CCF-469F-9650-7F314DBAB6BB"
      },
      {
        "type": "KMXMDMAnaltyics",
        "value": "kmxProfileScore~JmDMmON"
      },
      {
        "type": "crmId",
        "value": "0016R000036MSFsQAO"
      },
      {
        "type": "buysCustomerId",
        "value": "debb28de-0732-4564-ba0c-7e6fbd697eee"
      },
      {
        "type": "storeCustomerId",
        "value": "558081",
        "meta": {
          "key": "locationId",
          "value": "7177"
        }
      }
    ]
  },
  "id": "7859f9d9-f2f5-4097-bac1-73cb9a124a25"
}
October 7, 2021 7:57 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/2352071491400",
  "subject": "2352071491400",
  "time": "2021-10-07T11:57:10.1653018Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "2352071491400",
    "sourceDateTimeUtc": "2021-10-07T11:56:43+00:00",
    "stockNumber": "21219019",
    "reservationId": "9249c71b-09e6-4691-b9ae-76d6b4ed915e",
    "identity": [
      {
        "type": "ciamId",
        "value": "66796741-5BD1-407D-8757-B2FCB8563BCA"
      },
      {
        "type": "storeCustomerId",
        "value": "214941",
        "meta": {
          "key": "locationId",
          "value": "7192"
        }
      },
      {
        "type": "crmId",
        "value": "0016R000036Oay1QAC"
      }
    ]
  },
  "id": "11d6e018-6a66-4199-a51d-2220e352c1d4"
}
October 7, 2021 7:55 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.interaction.reservation.created.v1",
  "source": "https://apis-mtls.carmax.com/mdm-interaction-v1/interactions/812218007361",
  "subject": "812218007361",
  "time": "2021-10-07T11:55:13.3421301Z",
  "dataContentType": "application/json",
  "data": {
    "interactionId": "812218007361",
    "sourceDateTimeUtc": "2021-10-07T11:54:48+00:00",
    "stockNumber": "20383717",
    "reservationId": "b3da4cb1-263a-478f-a7a8-c6fd67e0e483",
    "identity": [
      {
        "type": "ciamId",
        "value": "D5A5F88D-B83C-4923-B958-05959A229353"
      },
      {
        "type": "storeCustomerId",
        "value": "43027",
        "meta": {
          "key": "locationId",
          "value": "6138"
        }
      }
    ]
  },
  "id": "64b5176b-4490-44d0-8ecd-536e117dd014"
}'''

# COMMAND ----------

sample_json = json.loads('[' + re.sub('October \d. \d{4} \d{1,2}:\d{2} AM', ', ', sample_string) + ']')

# COMMAND ----------

def parse_identity_array(id_arr):
  id_dict = {entry['type']: entry['value'] for entry in id_arr}
  if 'storeCustomerId' in id_dict.keys():
    store_loc_num = [entry['meta']['value'] for entry in id_arr if entry['type'] == 'storeCustomerId'][0]
    id_dict['storeCustomerIdLocationId'] = store_loc_num
  return id_dict

def flatten_obj(dct):
  new_dct = dct
  new_dct['data']['identity'] = parse_identity_array(dct['data']['identity'])
  return new_dct

# COMMAND ----------

sample_json_flattened = []

for obj in sample_json:
  sample_json_flattened.append(flatten_obj(obj))

# COMMAND ----------

#id type prevalence
id_types = []
for obj in sample_json_flattened:
  id_types.extend(obj['data']['identity'].keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

#data key prevalence
id_types = []
for obj in sample_json_flattened:
  id_types.extend(obj['data'].keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

#obj key prevalence
id_types = []
for obj in sample_json_flattened:
  id_types.extend(obj.keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Event: Maxcare Selected
# MAGIC ```
# MAGIC {
# MAGIC   "specVersion": "1.0",
# MAGIC   "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
# MAGIC   "source": "https://vehicleorder-service.buys.carmax.com",
# MAGIC   "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
# MAGIC   "time": "2021-10-07T18:16:06.6199065Z",
# MAGIC   "dataContentType": "application/json",
# MAGIC   "data": {
# MAGIC     "Identities": [
# MAGIC       {
# MAGIC         "Rel": "NotSet",
# MAGIC         "Type": "CiamId",
# MAGIC         "Value": null
# MAGIC       },
# MAGIC       {
# MAGIC         "Rel": "NotSet",
# MAGIC         "Type": "CrmId",
# MAGIC         "Value": "0016R000036OfMqQAK"
# MAGIC       },
# MAGIC       {
# MAGIC         "Rel": "FirstAssigned",
# MAGIC         "Type": "AssociateId",
# MAGIC         "Value": "262957"
# MAGIC       }
# MAGIC     ],
# MAGIC     "StockNumber": "20946219",
# MAGIC     "VehicleOrderId": "b085a86e-ac88-4b1a-a8cb-eca8a131519a"
# MAGIC   },
# MAGIC   "id": "ee9decbed04c442bbdbffec164417001"
# MAGIC }
# MAGIC ```

# COMMAND ----------

maxcare_sample_string = '''
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T18:16:06.6199065Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": null
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036OfMqQAK"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "262957"
      }
    ],
    "StockNumber": "20946219",
    "VehicleOrderId": "b085a86e-ac88-4b1a-a8cb-eca8a131519a"
  },
  "id": "ee9decbed04c442bbdbffec164417001"
}
October 7, 2021 2:06 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T18:06:51.0141884Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "f44b7467-fb86-49c9-b9e0-f430be3118ce"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21127757",
    "VehicleOrderId": "7d13239d-de75-461a-9f65-9365afbb40c9"
  },
  "id": "184700395ec64ec9a80c7a84dd6e8a2c"
}
October 7, 2021 1:55 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:55:11.0448425Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "c26ccf44-069b-45e4-b586-59e241b07cb7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "255456"
      }
    ],
    "StockNumber": "21194789",
    "VehicleOrderId": "2f6c1b1f-85a4-43af-92a0-2370997a5c5c"
  },
  "id": "500ac765eaa4442285e087258a795487"
}
October 7, 2021 1:54 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:54:26.3067409Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "afb3dd41-f202-4f7d-becb-6d4dc99558e8"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20693464",
    "VehicleOrderId": "aaa1da68-5478-4708-977a-4674f0d24046"
  },
  "id": "95f44790c4704c4cae05ad63ad75b74a"
}
October 7, 2021 1:48 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:48:30.7417821Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "4508b6d0-9e11-4396-ae55-85756d8370b6"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "262957"
      }
    ],
    "StockNumber": "20946219",
    "VehicleOrderId": "84a67222-163a-49db-ab66-70980489614d"
  },
  "id": "cd92078d20ce4223840e5a9c52ed58be"
}
October 7, 2021 1:43 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:43:40.094753Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0ad98d1d-60b9-4d3c-8d5b-e147d5b558fc"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21248438",
    "VehicleOrderId": "a8e9447a-9afc-48e7-adde-ea95c8d7726e"
  },
  "id": "f5e2bca6bea64cac9b6bd1389f699554"
}
October 7, 2021 1:43 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:43:02.2328346Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d9f49666-89a9-4e87-9ef3-b6c04075af0d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256241"
      }
    ],
    "StockNumber": "21038225",
    "VehicleOrderId": "56ba9cb9-103b-4d30-b650-07c0b9ecfdd1"
  },
  "id": "734db0f5c81d4adab36a7e022076e6fa"
}
October 7, 2021 1:41 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:41:00.0152087Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "bf095963-523e-4675-a52f-94830b884568"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20820702",
    "VehicleOrderId": "58d4b5e2-de20-4d72-a25d-f91050c9fbf0"
  },
  "id": "b315c9ff8c63400588a07c2ccd2ebebb"
}
October 7, 2021 1:37 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:37:20.5695797Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "c26ccf44-069b-45e4-b586-59e241b07cb7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "255456"
      }
    ],
    "StockNumber": "21194789",
    "VehicleOrderId": "2f6c1b1f-85a4-43af-92a0-2370997a5c5c"
  },
  "id": "6271a8a22216421db140360687dabe21"
}
October 7, 2021 1:35 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:35:09.1333961Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "bb723d0f-f9f1-48e6-bd86-a12630ef508e"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20564728",
    "VehicleOrderId": "862bac05-90ea-40e8-8324-4a76febc0e57"
  },
  "id": "d735dce923cc46aa8b6bc3ede4861f2b"
}
October 7, 2021 1:33 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:33:26.9407307Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "f7dc203f-0e4a-4b8e-8c3f-333d19c2fe22"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "182988"
      }
    ],
    "StockNumber": "21236197",
    "VehicleOrderId": "8eb79bab-f9f4-493e-9089-aad84f2c78ab"
  },
  "id": "cf91304dcbc041e4a22516350ea199cb"
}
October 7, 2021 1:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T17:15:59.5611794Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "96eaa181-138b-4791-bdb1-846f751d8aa1"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036NVCQQA4"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "253559"
      }
    ],
    "StockNumber": "20903988",
    "VehicleOrderId": "4286f508-0375-46fc-b3b2-ac53b9502482"
  },
  "id": "53cf441f3a904eb78ad16edc757c1d0e"
}
October 7, 2021 12:55 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:55:35.6547851Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1b88ef79-8a6a-4623-a3e2-237b0e61dbf9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036MhiyQAC"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "252171"
      }
    ],
    "StockNumber": "20541520",
    "VehicleOrderId": "b9849a72-b453-4d58-b2d4-a0769cc05b97"
  },
  "id": "076ee9d9fd0c4629a6570b1cfc763df7"
}
October 7, 2021 12:49 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:49:54.3198728Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "47f20b84-f284-4c40-b01f-5b978ce86b38"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21176580",
    "VehicleOrderId": "e4cb025e-0ae7-4b9d-b35d-09e178bb9821"
  },
  "id": "cf1f79db68b9445e948e8df2dc694d2d"
}
October 7, 2021 12:46 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:46:25.7779473Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d9f49666-89a9-4e87-9ef3-b6c04075af0d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256241"
      }
    ],
    "StockNumber": "21038225",
    "VehicleOrderId": "56ba9cb9-103b-4d30-b650-07c0b9ecfdd1"
  },
  "id": "8baafe9c13fc46f689d8338d9f926b3e"
}
October 7, 2021 12:45 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:45:16.1816806Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "c0aecc0e-e94a-41c3-a00f-2b094e538a1c"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21233370",
    "VehicleOrderId": "27a0e93d-0c50-4999-b0a8-bbc25e803992"
  },
  "id": "1f208819add04fee884f2e9c9b89192e"
}
October 7, 2021 12:43 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:43:59.2203674Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "ead617d2-1c52-4ecf-8d9b-d8812d15935a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20656567",
    "VehicleOrderId": "b8784985-31a7-4fd1-9b47-6aa9be29028b"
  },
  "id": "fdbb754774844b5c87e326b77abb0129"
}
October 7, 2021 12:34 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:34:51.2464233Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a663f61c-98e0-410a-8e54-0e568aa64e90"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21121674",
    "VehicleOrderId": "40a3b4a8-2a0e-43f2-ac7f-97d75513c7d8"
  },
  "id": "e7e864336bb84c43bb7f456c08378200"
}
October 7, 2021 12:33 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:33:06.4529535Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "f4210dea-f650-458c-893a-68073ed808aa"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "189653"
      }
    ],
    "StockNumber": "21162560",
    "VehicleOrderId": "96e1d2d2-7749-485d-be40-02396e58a786"
  },
  "id": "5d661d597b7b4c6b8dcfcf42e9cc47c8"
}
October 7, 2021 12:25 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:25:25.3798216Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "96eaa181-138b-4791-bdb1-846f751d8aa1"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036NVCQQA4"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "253559"
      }
    ],
    "StockNumber": "20903988",
    "VehicleOrderId": "4286f508-0375-46fc-b3b2-ac53b9502482"
  },
  "id": "d46f2a6bf83e43dba3bf9fdcf501609e"
}
October 7, 2021 12:14 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T16:14:19.4229488Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "aa01e261-a72c-4531-a9a0-90a9f08dba64"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "252399"
      }
    ],
    "StockNumber": "20502150",
    "VehicleOrderId": "d574a794-5c27-4e6a-9c1c-5ffd2751bf3e"
  },
  "id": "8ca8304fbdf1495f81c95169382ea711"
}
October 7, 2021 11:45 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T15:45:25.7220271Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "3c5efb85-1edb-48bf-92d7-bc6775ddc138"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21284097",
    "VehicleOrderId": "a8c453d3-5e04-45f3-847f-cd81d518a3f4"
  },
  "id": "bf938de1d6d1413cb744690c054d627b"
}
October 7, 2021 11:02 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T15:02:50.3109036Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0ccf9336-7fbc-4687-8c43-dd649abd6f1c"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "251989"
      }
    ],
    "StockNumber": "20837831",
    "VehicleOrderId": "e395b884-17c6-4b83-af16-27967c1b9e63"
  },
  "id": "01bad0f2829448b9a88c83a29882125d"
}
October 7, 2021 11:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T15:01:34.4825502Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "aa01e261-a72c-4531-a9a0-90a9f08dba64"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20502150",
    "VehicleOrderId": "d574a794-5c27-4e6a-9c1c-5ffd2751bf3e"
  },
  "id": "3768d913e9784921ab17627d6beb5cc8"
}
October 7, 2021 10:56 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T14:56:53.304649Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "8a64ac76-fe00-4225-8667-6636b927ebe9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21128841",
    "VehicleOrderId": "bd1b7f9a-c290-4c61-8cb4-a59934c58248"
  },
  "id": "a30f6ddb8c5d4debbc29032cd0c3bc12"
}
October 7, 2021 10:52 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T14:52:35.9274822Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "cee8de3c-d51e-4eb0-bdc4-ade55af403d3"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20419121",
    "VehicleOrderId": "7077df3e-1b71-442a-ad79-0581fb4fb961"
  },
  "id": "099e8a258ae74217b453eed88b690f03"
}
October 7, 2021 10:52 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T14:52:31.5575989Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "139bc760-70e2-443b-be1d-f23c81606b56"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21224207",
    "VehicleOrderId": "fe011292-0405-49ab-8ee0-60df3dff0cfc"
  },
  "id": "af3f10db583d433aa9ea179132a1ec04"
}
October 7, 2021 10:49 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T14:49:02.6168144Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "139bc760-70e2-443b-be1d-f23c81606b56"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21224207",
    "VehicleOrderId": "fe011292-0405-49ab-8ee0-60df3dff0cfc"
  },
  "id": "56af42e8889b4536a0f22a4d0bcc28f9"
}
October 7, 2021 10:20 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T14:20:25.6085637Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "02587ce3-0bf1-4c2d-983e-00e4b9211ebc"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20797750",
    "VehicleOrderId": "d84493c7-5bbb-43a8-8606-86158e8d982b"
  },
  "id": "f6280dee37d443be9a4dc1c76b860654"
}
October 7, 2021 9:54 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T13:54:05.8162513Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "3348e14d-1fd3-495a-bf73-a3187a4d9f0b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036ONKdQAO"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "187144"
      }
    ],
    "StockNumber": "21356017",
    "VehicleOrderId": "73d53cf7-cfd2-408b-96ea-48990f3e9d63"
  },
  "id": "5182b1c3bb554a1aa480a685bb030016"
}
October 7, 2021 9:33 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T13:33:09.2503617Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d55f8ea0-c2f3-4367-9d7b-956114f544fe"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21421675",
    "VehicleOrderId": "5f2a1ce4-2552-41a6-aebb-f2d34b67bd28"
  },
  "id": "8dc56d53701d47e3a3b20ad3cc598365"
}
October 7, 2021 9:29 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T13:29:11.6431759Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d55f8ea0-c2f3-4367-9d7b-956114f544fe"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21421675",
    "VehicleOrderId": "5f2a1ce4-2552-41a6-aebb-f2d34b67bd28"
  },
  "id": "203a4ee9b9b14a47930577d72cbddfc8"
}
October 7, 2021 8:26 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T12:26:07.1067794Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b1a34728-81a3-4dc4-8d89-aabd0069ab3a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256304"
      }
    ],
    "StockNumber": "21065111",
    "VehicleOrderId": "6ec630ab-81f8-40e6-81e6-6104a972cafa"
  },
  "id": "0fd1be62fcac45e7be193d93c5536d2a"
}
October 7, 2021 8:10 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T12:10:20.4345281Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "119d514c-15bb-4aaa-a7b6-fd600a0dd129"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21110174",
    "VehicleOrderId": "ad36b399-c9d1-49d3-8a95-e52329749e0f"
  },
  "id": "d6db5b266749425ab200f9f6f3fbbc83"
}
October 7, 2021 7:30 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T11:30:29.9181579Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a239e869-cf1a-4b89-aef8-f79c9126e032"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21306009",
    "VehicleOrderId": "2959cd86-09ca-4be9-8920-0f1d3d76e89b"
  },
  "id": "b6dbff3b65cd45358fb5dcb126ac5e28"
}
October 7, 2021 3:41 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T07:41:19.5081405Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d9f49666-89a9-4e87-9ef3-b6c04075af0d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256241"
      }
    ],
    "StockNumber": "21038225",
    "VehicleOrderId": "56ba9cb9-103b-4d30-b650-07c0b9ecfdd1"
  },
  "id": "107794b36c2b4dafbff80abfa1c9ca70"
}
October 7, 2021 3:32 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T07:32:18.105583Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "53f00b12-ddcd-4d0b-8a01-ca21b73834d6"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21199240",
    "VehicleOrderId": "a2d8123f-04e9-4d5a-b7a1-ca2879006c15"
  },
  "id": "8b5d15dbf5d148c6a88f3edb9d5d176e"
}
October 7, 2021 2:53 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T06:52:59.8741726Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d9f49666-89a9-4e87-9ef3-b6c04075af0d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256241"
      }
    ],
    "StockNumber": "21038225",
    "VehicleOrderId": "56ba9cb9-103b-4d30-b650-07c0b9ecfdd1"
  },
  "id": "62f1b1aed8994686bfa3935a5fd5659c"
}
October 7, 2021 2:30 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T06:30:37.3078992Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "14ac4ca1-f131-482a-b736-89521cdd9b64"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21196011",
    "VehicleOrderId": "12196c4f-50f4-4954-b60b-ffe425580887"
  },
  "id": "dc1767c8bea740f79bef117b31bd9195"
}
October 7, 2021 2:09 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T06:09:58.078166Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "922532ba-821f-4154-a0d6-ca4481e4545c"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21189059",
    "VehicleOrderId": "b6d4eb4f-06f3-4e33-b48d-cfc8cfa2a3a3"
  },
  "id": "309a0dbd5954401696b1819b5e6ca366"
}
October 7, 2021 2:09 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T06:09:37.3274093Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6418e042-2de0-45b4-9f37-26f46967daa5"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20574326",
    "VehicleOrderId": "fd2e83c8-84c8-4792-bd30-5d082612cf59"
  },
  "id": "3dcbb102bdba4d0d962430e0e88dd0a7"
}
October 7, 2021 1:29 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T05:29:53.9002583Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a74091bd-2222-4fde-961b-1cb2294a6ade"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21345427",
    "VehicleOrderId": "d35e7d04-f114-45cb-b584-5b080f494b3b"
  },
  "id": "2c9905a0efdc40319edaf246bcb4ddda"
}
October 7, 2021 1:13 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T05:13:21.0666926Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b1a34728-81a3-4dc4-8d89-aabd0069ab3a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21065111",
    "VehicleOrderId": "6ec630ab-81f8-40e6-81e6-6104a972cafa"
  },
  "id": "c10cb712966a4293bf00276e3d8a3360"
}
October 7, 2021 1:02 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T05:02:10.1789788Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0259f892-7efa-42a5-a2d8-b83ed4d705c9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20931817",
    "VehicleOrderId": "ae7d23b1-dc27-46f3-9a45-ded3a912fa10"
  },
  "id": "21e0d3b639904ef080fdbfaace50ea25"
}
October 7, 2021 1:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T05:01:50.1821157Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a43ae577-37a4-4195-b8c9-aff7c26014ef"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21324611",
    "VehicleOrderId": "a033a80a-53d0-4ca6-8956-75223801d24a"
  },
  "id": "2dcc4554743c4ae5984362ebd0733206"
}
October 7, 2021 12:54 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T04:54:07.9245624Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1b834c8f-136b-47ef-8664-4b785ce5d6c7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21090579",
    "VehicleOrderId": "3c0dfba6-c3e1-4cb6-a91e-8ba5285cd7bf"
  },
  "id": "3503ca873f3240068154bcc1539894ad"
}
October 7, 2021 12:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T04:28:37.8336732Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d9f49666-89a9-4e87-9ef3-b6c04075af0d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256241"
      }
    ],
    "StockNumber": "21038225",
    "VehicleOrderId": "56ba9cb9-103b-4d30-b650-07c0b9ecfdd1"
  },
  "id": "44a0ea6dbf634dc1aeb9434ba6560a25"
}
October 7, 2021 12:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T04:28:09.2092066Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d9f49666-89a9-4e87-9ef3-b6c04075af0d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256241"
      }
    ],
    "StockNumber": "21038225",
    "VehicleOrderId": "56ba9cb9-103b-4d30-b650-07c0b9ecfdd1"
  },
  "id": "fd6557221a074ca38e32e13494eec986"
}
October 7, 2021 12:03 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T04:03:01.7859904Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d2977050-95ea-489f-9bdd-03c3c3413b38"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20928958",
    "VehicleOrderId": "5de5cd7f-a8f0-48a1-9ccf-76f210d183de"
  },
  "id": "65ce9c11c84e45749ca00687c825fe56"
}
October 7, 2021 12:00 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T04:00:01.4712149Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d2977050-95ea-489f-9bdd-03c3c3413b38"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20928958",
    "VehicleOrderId": "5de5cd7f-a8f0-48a1-9ccf-76f210d183de"
  },
  "id": "1969bf2239054b66a395972519f6cedc"
}
October 6, 2021 11:45 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T03:45:38.7546801Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b5959157-ac3f-458e-924d-af22c1fddfe9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21192026",
    "VehicleOrderId": "84944583-a98d-4c6e-b9bc-d7b675f698c5"
  },
  "id": "d072cdef7ac04913af6c811ce16ebdd9"
}
October 6, 2021 11:36 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T03:36:04.4048904Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "92cd081a-e8ad-4112-b695-5cc60e991dea"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21233074",
    "VehicleOrderId": "e7279ee8-6ef4-4a21-95d9-45ea4f7b8e7a"
  },
  "id": "7dce467c6064422589579ee70d0c12e1"
}
October 6, 2021 11:13 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T03:13:52.2460068Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1e588b43-65ee-451b-85da-a2b8014be931"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21018965",
    "VehicleOrderId": "f3cfbba9-378d-467d-b593-ff5a55f59414"
  },
  "id": "c6d18f29563b4512be78848fa35496c6"
}
October 6, 2021 11:12 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T03:12:30.516321Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": null
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0011C00002pMdY1QAK"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "261503"
      }
    ],
    "StockNumber": "20814510",
    "VehicleOrderId": "8a718789-66b1-4bfc-a5aa-bbe30c936718"
  },
  "id": "fc08210d43614f91aed729eb1813a13f"
}
October 6, 2021 10:40 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T02:40:47.5211725Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "aac56aa4-da44-4279-96dc-1252930cb3ae"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "265895"
      }
    ],
    "StockNumber": "20286384",
    "VehicleOrderId": "ecf60a58-c7a9-448b-b958-47bef133ce2e"
  },
  "id": "5f3fda2487d84ec89707ddeebe1deeb1"
}
October 6, 2021 10:37 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T02:37:42.7126529Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "caaa6e5f-19e1-4beb-a154-3e00622f9f97"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21205629",
    "VehicleOrderId": "fccb1fa1-d12d-4cf8-ae6d-450c778c9b0f"
  },
  "id": "dd5b804906a24145be096d22b2928816"
}
October 6, 2021 10:34 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T02:34:01.8359454Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "17f8b5b9-eeab-45ad-887d-76e6c0319637"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "257867"
      }
    ],
    "StockNumber": "21302069",
    "VehicleOrderId": "6044e857-0d6a-4553-89b2-291d4312d4d2"
  },
  "id": "ab1062da50364f28a1362c24cd35e2b7"
}
October 6, 2021 10:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T02:22:06.8343818Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "17f8b5b9-eeab-45ad-887d-76e6c0319637"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21302069",
    "VehicleOrderId": "6044e857-0d6a-4553-89b2-291d4312d4d2"
  },
  "id": "80c6e7455b784e6988ead1784113ed64"
}
October 6, 2021 10:12 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T02:12:47.5775493Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "5d0c39d2-3369-4724-9b5b-b4f1d9f99c24"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20904549",
    "VehicleOrderId": "f5421823-3e23-4f58-b805-856161b3ea0d"
  },
  "id": "2dbae9a83a78414e8951b76b4e398f9b"
}
October 6, 2021 10:11 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T02:11:19.2033349Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "5d0c39d2-3369-4724-9b5b-b4f1d9f99c24"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20904549",
    "VehicleOrderId": "f5421823-3e23-4f58-b805-856161b3ea0d"
  },
  "id": "a8d144a7e6d542b7b51ffb912f54bff6"
}
October 6, 2021 10:07 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T02:07:10.3779684Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "96eaa181-138b-4791-bdb1-846f751d8aa1"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036NVCQQA4"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "253559"
      }
    ],
    "StockNumber": "20903988",
    "VehicleOrderId": "4286f508-0375-46fc-b3b2-ac53b9502482"
  },
  "id": "7fb0d339c9644d3785adbede91702bc4"
}
October 6, 2021 9:59 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T01:59:40.1149323Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a98c52c1-50ca-4266-b126-de93620ecdbc"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21212850",
    "VehicleOrderId": "6d239f0d-5be6-48f5-b4db-5af445ffbf5e"
  },
  "id": "dbfa2b46498a462c970df70ea657750a"
}
October 6, 2021 9:55 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T01:55:42.840594Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "082fc9ac-f88d-48bc-a627-e92a7757ff3a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21167899",
    "VehicleOrderId": "d08e373b-9efa-4638-a378-a3d61f7ad091"
  },
  "id": "375f7507c8dc43098e0c2bb2a0eab653"
}
October 6, 2021 9:49 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T01:49:05.4838351Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6c32dae4-b896-4f29-9418-67ec89f5e31b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21174423",
    "VehicleOrderId": "149e8afc-3732-40a9-95f8-ebfd5fa4f305"
  },
  "id": "38dd111f875a4abbbc027f9467922f05"
}
October 6, 2021 9:38 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T01:38:04.6602054Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "4bac16f4-d5f3-408b-94a1-3cf48a777b42"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21095453",
    "VehicleOrderId": "f3a9c692-71e3-43ac-9527-310a52623ca0"
  },
  "id": "2f88b21bab4b4a0eb9165868b589977e"
}
October 6, 2021 9:37 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T01:37:50.4625084Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "2c5f7832-9bef-4c2b-b2f2-7f59562cdd54"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20616692",
    "VehicleOrderId": "63faf329-8774-4e70-8a41-590654c29575"
  },
  "id": "68868af828084d7c81547a54bd1caed3"
}
October 6, 2021 9:26 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T01:26:10.9129428Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6cdce468-16a4-4b17-ac68-a33d00d0492a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21220603",
    "VehicleOrderId": "8d052881-f95e-46b4-955f-986411112f97"
  },
  "id": "15a9900f029e49e58ea4feb70bfd0790"
}
October 6, 2021 8:58 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T00:58:42.5565208Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6bde910f-a072-43c5-87df-9352d38ba162"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21385363",
    "VehicleOrderId": "a4b70307-fe80-4ee2-8239-e8c31889ed4c"
  },
  "id": "3c22a89a5ea241f895fbe51615c96916"
}
October 6, 2021 8:58 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T00:58:10.6989659Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6bde910f-a072-43c5-87df-9352d38ba162"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21385363",
    "VehicleOrderId": "a4b70307-fe80-4ee2-8239-e8c31889ed4c"
  },
  "id": "5aadd07527f5445ca9380b9374793c3b"
}
October 6, 2021 8:53 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T00:53:51.7274736Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "2bd1d317-739d-4592-9f2d-4f84d007902b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0011C00001tz096QAA"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "259493"
      }
    ],
    "StockNumber": "20903492",
    "VehicleOrderId": "bf3528d7-459b-4de1-9a9b-579146d9598b"
  },
  "id": "d9f62f6536a4414186b8884ff17d96f1"
}
October 6, 2021 8:45 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T00:45:20.804661Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "08a2b7c4-3571-47ad-b7af-3b9b4d396d59"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21353061",
    "VehicleOrderId": "aacd8677-cc86-4a80-a6db-b3ab1beed774"
  },
  "id": "b73e3fe3d1f84f8ead003a2718107d67"
}
October 6, 2021 8:44 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T00:44:09.0050953Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "8798a29e-631d-4961-9336-02dd13aac93a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0011C00002xyceXQAQ"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "239900"
      }
    ],
    "StockNumber": "20968728",
    "VehicleOrderId": "940f19c1-5ba0-44c2-8e36-70435390d1e4"
  },
  "id": "5ee7912deee64c6587ce97f3163a3cb6"
}
October 6, 2021 8:24 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-07T00:24:23.2749252Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a11aad5c-2681-43e4-8049-5d269da93828"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21132710",
    "VehicleOrderId": "f1158052-7693-4491-88c6-6aa40c29b3b8"
  },
  "id": "ef34d1f315ab4209b6c43a1bdac5d1d2"
}
October 6, 2021 7:52 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T23:52:18.637934Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "399aee67-91e7-4ef4-8212-147a8bfd63c2"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20927977",
    "VehicleOrderId": "4df6e1d3-2c87-431e-bdae-26b6be4eff12"
  },
  "id": "39fc2aaad215472aab53dff477134d02"
}
October 6, 2021 7:51 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T23:51:51.9926791Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "82fae206-1cff-4090-aef2-10ae99064e82"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "214917"
      }
    ],
    "StockNumber": "20916256",
    "VehicleOrderId": "998e26d1-16a7-4ad4-96b1-04eae19f0c0d"
  },
  "id": "2d478aef91674e4b85898b035812924a"
}
October 6, 2021 7:49 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T23:49:05.6794621Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "ae0fca6a-2ab9-40f5-b2f4-712a2dd67eb2"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20936229",
    "VehicleOrderId": "b62d08cb-f873-43e1-84f9-f58c8d0b7555"
  },
  "id": "de7ef58b84c84c35b9cf0017e1f2d969"
}
October 6, 2021 7:48 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T23:48:16.5033873Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "2330833a-1e0f-48da-8ff3-b75ef233f264"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "264667"
      }
    ],
    "StockNumber": "21077061",
    "VehicleOrderId": "daf7af5b-09fc-472a-8d42-5ff9dce4d4c9"
  },
  "id": "5e82e8d826af46e7a5527f557a46332a"
}
October 6, 2021 7:26 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T23:26:43.9731057Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "cf6e8577-f885-486f-9cfb-95304c5c76e7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21273160",
    "VehicleOrderId": "6b034096-fcef-476e-b98e-3c36e1f45ea6"
  },
  "id": "7327a90625b3437dacf17388786d373d"
}
October 6, 2021 6:52 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T22:52:52.5245018Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "e83bf7b1-fd70-4524-af7d-099b6fd2605b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "266114"
      }
    ],
    "StockNumber": "21139286",
    "VehicleOrderId": "49a3deed-9b2e-472a-a252-570aeff0e8dd"
  },
  "id": "44633e8ae45a461a9189dbf133d68cff"
}
October 6, 2021 6:48 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T22:48:46.9931063Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1b355441-7534-464c-8e4f-1d84fb080b02"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21264491",
    "VehicleOrderId": "cb6a8059-8a1b-490f-ab06-8d583234ed28"
  },
  "id": "9a695b7ef90e4fbca096176d6a3ed505"
}
October 6, 2021 6:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T22:16:15.03039Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0c183320-daf6-4b3d-a462-2641694f3769"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21352567",
    "VehicleOrderId": "506e6167-2eb1-4749-b904-a7e8b3ac4b84"
  },
  "id": "78c84bc4412745a89670e05dc989c825"
}
October 6, 2021 5:58 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T21:58:30.6733902Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "5f82a1f7-f6c3-47aa-8def-3f3658a4edd8"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "240655"
      }
    ],
    "StockNumber": "21004920",
    "VehicleOrderId": "14fb5d7a-f4d5-4630-9be6-435dfb735d7b"
  },
  "id": "b9059affb1a54e4282d95e2c52b7621b"
}
October 6, 2021 5:50 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T21:50:46.1481533Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "90c41749-006b-408f-8198-e549d9ac9e8f"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "202922"
      }
    ],
    "StockNumber": "21218241",
    "VehicleOrderId": "9ff5e822-bb90-4e67-8aef-48339393218a"
  },
  "id": "532821656b894503bbf4894f70541872"
}
October 6, 2021 5:49 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T21:49:15.213818Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a1546c70-a5be-484b-8e71-c511519f1b6f"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "215538"
      }
    ],
    "StockNumber": "21272637",
    "VehicleOrderId": "582e9946-bcda-44a9-9a8e-2af6ebbc1735"
  },
  "id": "7eec55577517401491f34b7c6aad83ae"
}
October 6, 2021 5:45 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T21:45:23.2266395Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "723d71ea-403a-4d00-925d-69943d316c34"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21146082",
    "VehicleOrderId": "67184b82-d335-4602-8090-84c3135453ea"
  },
  "id": "34ac047bd3c9448fad2437426e6a1798"
}
October 6, 2021 5:29 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T21:29:44.8214307Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "cf41e327-7c6a-4a33-8ef8-e14f37279b0a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21169331",
    "VehicleOrderId": "85a8c2ed-1090-4a6f-a4a8-25c16cd29b4d"
  },
  "id": "bffc6c64a7c94295b509040d1f522fbe"
}
October 6, 2021 5:11 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T21:11:25.0686131Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "bc5462b4-3f2f-498f-8761-c36bd56ac554"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "254581"
      }
    ],
    "StockNumber": "21353063",
    "VehicleOrderId": "77e319a1-41b5-43e6-b7cd-63e34ec43bb4"
  },
  "id": "c3b1b846289d461f9f1aca1eb4c0b700"
}
October 6, 2021 4:35 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T20:35:19.9677475Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d876c971-ba8a-40b0-88a7-36ad8778267d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036OJbVQAW"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "189590"
      }
    ],
    "StockNumber": "21003888",
    "VehicleOrderId": "c394d90c-c2a6-4c57-abb9-cd6159655888"
  },
  "id": "bd4f309bb9d64dc98fc73127cbc3c154"
}
October 6, 2021 4:32 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T20:32:24.0562429Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "60615693-bb4d-4e12-95f5-98df8edeb99d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20904278",
    "VehicleOrderId": "2432e57b-7222-441f-a1bf-8c17c2f9024a"
  },
  "id": "71b2d25de8d14b57a02fccfe91406586"
}
October 6, 2021 4:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T20:21:44.4074129Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "ebc6ca5e-da50-4d90-843f-7014002b377d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "251501"
      }
    ],
    "StockNumber": "21135165",
    "VehicleOrderId": "dedc1976-1d59-49db-b588-8fa93ae07833"
  },
  "id": "8efb8b994f954bb1bd41a5ededdc5d9c"
}
October 6, 2021 4:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T20:19:14.8576101Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "528ccf4a-9caa-491f-af78-1ca3e046afd2"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "126242"
      }
    ],
    "StockNumber": "20706675",
    "VehicleOrderId": "894f80b6-cd8b-4195-9b5b-b6f055285ea1"
  },
  "id": "11a7698ddc5b407893b750bbc6ce091d"
}
October 6, 2021 3:42 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:42:50.8622885Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "815013fd-47e5-4d21-9ef3-b37b27b70da6"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21161164",
    "VehicleOrderId": "4286e0d5-50d5-4626-b87b-f6ea0c04dbb2"
  },
  "id": "806f3fc3cacc4804aafccc66a7e93acc"
}
October 6, 2021 3:35 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:35:01.9953236Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "f001ae17-941b-4133-8723-a24301442434"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "252546"
      }
    ],
    "StockNumber": "21273200",
    "VehicleOrderId": "e4f1caae-dd0e-4a2d-b466-fcf6425e7b63"
  },
  "id": "e8b320681d39409887328cbf847d06e0"
}
October 6, 2021 3:33 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:33:50.5492193Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "2088d16e-cedb-4f9c-a1e0-6a472ee8f8f3"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "240172"
      }
    ],
    "StockNumber": "20637647",
    "VehicleOrderId": "77caec0e-e3bc-4c00-9abf-396fb3285857"
  },
  "id": "ffa337ce3304451ab0f3f8323f2f1eb5"
}
October 6, 2021 3:33 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:33:22.7860671Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "502930e6-5a68-4a9c-8ae0-4083a95ffa21"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21205738",
    "VehicleOrderId": "c495d1da-4b79-4066-9375-0028e427a6ae"
  },
  "id": "cfc845969938416e873c7f240aa00d1a"
}
October 6, 2021 3:26 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:26:37.730275Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "de49392a-8847-4866-9750-614af5b3ad46"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "224648"
      }
    ],
    "StockNumber": "21344919",
    "VehicleOrderId": "aecce4e4-21a7-4c06-978b-673c2685b1b3"
  },
  "id": "8ddbd26a64474f44ba5713271ece34ec"
}
October 6, 2021 3:26 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:26:03.0681702Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "81d972ad-6bf2-42b7-a33d-2973f2d1a704"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20877277",
    "VehicleOrderId": "f4645149-ad8f-4a6f-9b41-e096cfea9c64"
  },
  "id": "8e54c613a9584fc69fda1c7cdab7729a"
}
October 6, 2021 3:25 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:25:42.6120289Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "163f886c-2f07-4849-8c9a-76af817e77b9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "266925"
      }
    ],
    "StockNumber": "20689761",
    "VehicleOrderId": "f06ae437-d67a-4fe4-8ff0-ae6f65cbeb63"
  },
  "id": "1a6bf179d7bd4fc78be741a99f04d27c"
}
October 6, 2021 3:24 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:24:02.5971877Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "e3485ea5-8640-450e-931e-0fc8fbb9b1b8"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "265386"
      }
    ],
    "StockNumber": "20781050",
    "VehicleOrderId": "cbb3df84-443c-4351-b34b-8524d6c5fd4d"
  },
  "id": "10f32f9f9ba04638b75f36ab472e64b1"
}
October 6, 2021 3:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:20:10.0261866Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b1bd2c53-dac3-4598-b844-adb32a29ec93"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20948818",
    "VehicleOrderId": "cfc6ca67-d52e-41f8-8a20-40876456ad8c"
  },
  "id": "42f2ec487ead47b0bc9b4fb70ad37ae5"
}
October 6, 2021 3:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:18:46.149683Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "5f6ce4d4-985b-4a5b-aa23-63bfb7d11f97"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21156326",
    "VehicleOrderId": "ee6ef5a2-242a-459e-a741-1328088bb67f"
  },
  "id": "c2b376819b1a4a8d8de6f694af10b0d4"
}
October 6, 2021 3:13 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T19:13:34.4202948Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b1bd2c53-dac3-4598-b844-adb32a29ec93"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20948818",
    "VehicleOrderId": "cfc6ca67-d52e-41f8-8a20-40876456ad8c"
  },
  "id": "196eba3392e94217852d03d327671f42"
}
October 6, 2021 2:32 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T18:32:32.2249136Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7504fdd0-ecb8-458f-a8da-64f109614ede"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21258492",
    "VehicleOrderId": "4d35d718-dcc2-4aff-a105-e0311c17ec9d"
  },
  "id": "f60cb42ad3ea4630a8b831dc9fbc84b9"
}
October 6, 2021 2:31 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T18:31:01.0166886Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "22bdf2b3-0f6f-4bdb-9e04-f82329cc3e0d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "265386"
      }
    ],
    "StockNumber": "20859468",
    "VehicleOrderId": "c7b17e63-9ee0-4f1a-9356-eaa0a6e53d0c"
  },
  "id": "f85c39efe50947958f72809e5c51312b"
}
October 6, 2021 2:30 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T18:30:01.8518744Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "f0a956ae-1c94-4d19-a42b-9a3e0cc5bec5"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "250911"
      }
    ],
    "StockNumber": "20993049",
    "VehicleOrderId": "3208d1b2-094a-4039-ae2f-bb8a73171352"
  },
  "id": "8606187e2f61487ea5bb288ddc819bb4"
}
October 6, 2021 2:24 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T18:24:34.5411387Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "851ebd6a-8405-4925-8b5f-ddbc156776ec"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20665142",
    "VehicleOrderId": "9f081f11-e150-4a44-a520-75ff2af1f1ef"
  },
  "id": "d7c7b0c3913d44b49cbafd689ccd9ac9"
}
October 6, 2021 2:07 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T18:07:52.7445171Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "2330833a-1e0f-48da-8ff3-b75ef233f264"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21077061",
    "VehicleOrderId": "daf7af5b-09fc-472a-8d42-5ff9dce4d4c9"
  },
  "id": "88466b7c2a50439b93fc4539890fa81f"
}
October 6, 2021 2:05 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T18:05:43.3150716Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7e512365-7206-4fa1-9890-a00200d79e89"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21024287",
    "VehicleOrderId": "db1ebdea-c5d0-4303-884e-261956f1b37c"
  },
  "id": "2a30b606821f46499a239feace7b9f84"
}
October 6, 2021 1:54 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T17:54:04.3235989Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b789782a-a83b-4c63-be59-a3e90113fd87"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21164510",
    "VehicleOrderId": "f06d0e2e-4514-4a97-959a-2d6cf1948aff"
  },
  "id": "d6b7dc5871d74f85a015c1f3b78f97cf"
}
October 6, 2021 1:46 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T17:46:25.6264165Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "f0a956ae-1c94-4d19-a42b-9a3e0cc5bec5"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20993049",
    "VehicleOrderId": "3208d1b2-094a-4039-ae2f-bb8a73171352"
  },
  "id": "7cad7c1d18cf4d3691162b7c9d2f3aaf"
}
October 6, 2021 1:31 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T17:31:21.0299611Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "be456deb-55e3-4d0f-8df2-a2c000dda2c1"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21367559",
    "VehicleOrderId": "0bb08f90-a8db-4ba3-b0a6-2ba1c3b2936d"
  },
  "id": "6a9e5d37a38349fea8cf75372f3f69a1"
}
October 6, 2021 1:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T17:16:14.5924177Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "22bf2f35-917a-428e-916d-e68b818d977e"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036444nQAA"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "250637"
      }
    ],
    "StockNumber": "20916678",
    "VehicleOrderId": "f26f33c9-f6ed-4f0a-81e4-f465bc782f92"
  },
  "id": "9d47fda5b5b04d169c1aabfb912566a3"
}
October 6, 2021 1:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T17:15:15.7833Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "37e80ef0-b6db-4ef6-bc78-ca9a4ede0d22"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20029624",
    "VehicleOrderId": "275bed3c-1597-4d2e-abd1-48038d5e6422"
  },
  "id": "336d5166b0a943398450cebcc29bbb67"
}
October 6, 2021 1:11 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T17:11:27.5973338Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6e4ae5b1-85af-4e59-b2fa-a312016f0d1c"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21167266",
    "VehicleOrderId": "f66d02e9-8de7-43a9-919f-697cc68b0c04"
  },
  "id": "0ce9cee6226f4a9998e4b57dafc3e029"
}
October 6, 2021 12:58 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T16:58:29.8610306Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "36645ea7-6675-4878-a4c0-28ef4ddc40e7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "266172"
      }
    ],
    "StockNumber": "20946166",
    "VehicleOrderId": "78861cfd-d6f7-43e0-8c9b-0e6af60841e1"
  },
  "id": "64d7dc706082447dabdce464a125d5bc"
}
October 6, 2021 12:39 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T16:39:17.0783378Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "97dd7846-527b-448d-96f2-de8108ffc0aa"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20971169",
    "VehicleOrderId": "34b019c8-9fe9-43d0-9d4b-34e93e737101"
  },
  "id": "0805fbb759f647009fae2645da426e37"
}
October 6, 2021 12:24 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T16:24:27.548845Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "4bc0ff55-4840-44ff-a066-b4579dc6cd6a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21224246",
    "VehicleOrderId": "36c67d6a-8101-43d4-8f47-545449e18a20"
  },
  "id": "b3f751e4b8cb453d90ee2d9959cc0c5e"
}
October 6, 2021 12:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T16:21:13.3663852Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "88e8b16c-3d56-40cc-b91f-ac5949979b4d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "215790"
      }
    ],
    "StockNumber": "21121778",
    "VehicleOrderId": "49abf903-3344-4a2c-a531-d5812a20fb18"
  },
  "id": "5dbbeb0ec7804022962a8023dbf755e5"
}
October 6, 2021 12:14 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T16:14:26.1718259Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "2bd1d317-739d-4592-9f2d-4f84d007902b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0011C00001tz096QAA"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "259493"
      }
    ],
    "StockNumber": "20903492",
    "VehicleOrderId": "bf3528d7-459b-4de1-9a9b-579146d9598b"
  },
  "id": "2532d368bbf74f8aa2e152ba089c843c"
}
October 6, 2021 12:03 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T16:03:04.7997208Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "884ac9ce-2681-4984-aa3a-84bbf6360cf0"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21018852",
    "VehicleOrderId": "c4853d2e-0c48-493c-806e-7a873493fd67"
  },
  "id": "7141f082b70a48cea35b637bd106ab8d"
}
October 6, 2021 12:02 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T16:02:26.896153Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "94e9a130-3b95-4b58-8727-594e35013410"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "248906"
      }
    ],
    "StockNumber": "20931506",
    "VehicleOrderId": "a75e76ef-dd8c-4919-ac7e-438674ff1d05"
  },
  "id": "51d7c539a09b4784885918ceda5abd92"
}
October 6, 2021 11:53 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T15:53:17.3984883Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "19ea5a5d-611c-4b94-b621-fe0699f3d2b2"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "266984"
      }
    ],
    "StockNumber": "21344756",
    "VehicleOrderId": "5cced01b-3c3d-414a-998d-c8922cda9bd2"
  },
  "id": "09a08af83dd04acebb67e11a0e9fcb1c"
}
October 6, 2021 11:52 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T15:52:48.2579278Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "19ea5a5d-611c-4b94-b621-fe0699f3d2b2"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "266984"
      }
    ],
    "StockNumber": "21344756",
    "VehicleOrderId": "5cced01b-3c3d-414a-998d-c8922cda9bd2"
  },
  "id": "5b22c34da366409ca55b387833ad05c3"
}
October 6, 2021 11:40 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T15:40:12.5334253Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "88e8b16c-3d56-40cc-b91f-ac5949979b4d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "215790"
      }
    ],
    "StockNumber": "21121778",
    "VehicleOrderId": "49abf903-3344-4a2c-a531-d5812a20fb18"
  },
  "id": "8ecb53f66886410bb46ad7520b3f1ab2"
}
October 6, 2021 11:26 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T15:26:58.0282609Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "e04f7fa8-8c80-4edd-bd51-dbf08aa874ff"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036NisyQAC"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "264090"
      }
    ],
    "StockNumber": "21324210",
    "VehicleOrderId": "7336207a-a6a8-4c8a-a44a-23b82f8b1850"
  },
  "id": "aec284eaea13408aad3474db1e3fdd2e"
}
October 6, 2021 10:58 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T14:58:23.1774165Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "97dd7846-527b-448d-96f2-de8108ffc0aa"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20971169",
    "VehicleOrderId": "34b019c8-9fe9-43d0-9d4b-34e93e737101"
  },
  "id": "bd38dbeaf7d14ddc94bc9c7798ee3d36"
}
October 6, 2021 10:53 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T14:53:58.3936197Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d51a4277-d3e1-4f07-9efb-afe3100a1ffb"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21095455",
    "VehicleOrderId": "23967783-266c-44c1-b88f-0af35afe3d25"
  },
  "id": "5f1ee68562bd4cdbafca9ecee640d458"
}
October 6, 2021 10:50 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T14:50:14.4878856Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0c99b8ea-981b-41a9-adef-1bc738dbf516"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "255823"
      }
    ],
    "StockNumber": "20919537",
    "VehicleOrderId": "de21dc94-e2e5-4dd0-94e7-33011a193349"
  },
  "id": "783e69fe90a946c7a05bda547ad71153"
}
October 6, 2021 10:15 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T14:15:02.8735465Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6418e042-2de0-45b4-9f37-26f46967daa5"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20574326",
    "VehicleOrderId": "fd2e83c8-84c8-4792-bd30-5d082612cf59"
  },
  "id": "052507cc619a4b5cbdcd08ac8024f683"
}
October 6, 2021 9:47 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T13:47:37.4110185Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "603d9a27-96f2-4989-87ad-a47064eada43"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "250817"
      }
    ],
    "StockNumber": "21375249",
    "VehicleOrderId": "c47bd91a-cce5-48fa-84a6-b428fde48c67"
  },
  "id": "f62a32b6bca94c44873d1e8e69c9d6df"
}
October 6, 2021 9:20 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T13:20:23.2608166Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7d9aeef7-ccdb-4895-bb5e-5403610fdf9b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20848162",
    "VehicleOrderId": "8e2aac94-6859-4b49-ae46-1b8e18a082e0"
  },
  "id": "d8001b0395664c4da483af5ece898687"
}
October 6, 2021 9:19 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T13:19:40.6904695Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7d9aeef7-ccdb-4895-bb5e-5403610fdf9b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20848162",
    "VehicleOrderId": "8e2aac94-6859-4b49-ae46-1b8e18a082e0"
  },
  "id": "4b738ab9fa15449a9c6757577f39c55d"
}
October 6, 2021 7:58 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T11:58:48.18951Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "cb8ee1bc-9faf-4921-9770-8b7fe3ae701b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20242445",
    "VehicleOrderId": "d51a28a4-9bcf-4ffc-9c2d-76282e00a8f8"
  },
  "id": "d481daedb67641c88b95cc3e5762685d"
}
October 6, 2021 7:34 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T11:34:14.6287323Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "beff44ca-5cab-4245-82df-fe0ebcb72303"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21268310",
    "VehicleOrderId": "0d3b5a7a-950f-4728-a1b9-ba79c82c4b27"
  },
  "id": "a8efad0c2bd24063890e7cb5aa1a2a97"
}
October 6, 2021 3:05 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T07:05:59.5474006Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b04f37bf-cf8d-4891-8998-799b60e3a54a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21253082",
    "VehicleOrderId": "f906f83c-f455-44a2-b82e-b97542200e67"
  },
  "id": "7c3d08b1f3104fafb07a32ad49858c5f"
}
October 6, 2021 2:56 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T06:56:32.9216671Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "4bee301c-a227-40ea-8f06-734dad1cbfdd"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20819984",
    "VehicleOrderId": "ffe345a4-3bcb-4fc8-9cc8-a0cf1bf2813a"
  },
  "id": "7c715ebb3dc8442386aa77b15971fff1"
}
October 6, 2021 1:33 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T05:33:43.3420177Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0b022c90-3b69-4aab-8574-198108076eb0"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21179955",
    "VehicleOrderId": "47ec0eec-03ec-42b4-a2cd-2b757e9e168b"
  },
  "id": "5d13419196e3449a9106d7340286ea06"
}
October 6, 2021 1:27 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T05:27:16.8098539Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b476f728-aa84-43f0-920e-4b5303db501a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20657965",
    "VehicleOrderId": "49b15f13-f57b-45fa-9929-ff654d8abeda"
  },
  "id": "ec27427cd1fb45b38ecd104b6c59d8fb"
}
October 6, 2021 1:12 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T05:12:31.5573163Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d137c3b2-3cfe-4914-843c-05c806ae6af7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21346516",
    "VehicleOrderId": "6e5b2bdb-90e2-4188-916b-d43f2b7ae983"
  },
  "id": "2080055617154b2982edb8e3689b2fe4"
}
October 6, 2021 1:11 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T05:11:36.8222068Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d137c3b2-3cfe-4914-843c-05c806ae6af7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21346516",
    "VehicleOrderId": "6e5b2bdb-90e2-4188-916b-d43f2b7ae983"
  },
  "id": "4986d83da3a4414c9063cdf51434d6ce"
}
October 6, 2021 1:05 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T05:05:32.027616Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "88e8b16c-3d56-40cc-b91f-ac5949979b4d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21121778",
    "VehicleOrderId": "49abf903-3344-4a2c-a531-d5812a20fb18"
  },
  "id": "ceb8b4f9661f4ef5a08885c90f0c7328"
}
October 6, 2021 12:44 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:44:28.4461323Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "b1b3ca81-955b-4ee2-984e-aa40011c8d9e"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20714969",
    "VehicleOrderId": "d498144a-54be-4986-9dca-3b66d2c776af"
  },
  "id": "8b4ad5ca83424510bbce110ec7462e07"
}
October 6, 2021 12:37 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:37:12.4191261Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "2bc89be9-594f-4200-b561-36dea3c9e36a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21019556",
    "VehicleOrderId": "95941d92-7b26-4c88-a8eb-54ed9b764d2d"
  },
  "id": "c42d0a89a4014c16a25955f6230e1aa7"
}
October 6, 2021 12:31 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:31:03.2888821Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1d2b23aa-35e8-4e32-ad03-43a2a19815d7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21097498",
    "VehicleOrderId": "16d1bc9d-9f49-4560-9800-2fccb637d1a9"
  },
  "id": "4d9ef333e9564e54b8f5ca2cdbee2467"
}
October 6, 2021 12:29 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:29:58.7120972Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0c99b8ea-981b-41a9-adef-1bc738dbf516"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20919537",
    "VehicleOrderId": "de21dc94-e2e5-4dd0-94e7-33011a193349"
  },
  "id": "cd1f1be5d8f24c2084150c1b1bfd71a9"
}
October 6, 2021 12:28 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:28:37.5963854Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0c99b8ea-981b-41a9-adef-1bc738dbf516"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20919537",
    "VehicleOrderId": "de21dc94-e2e5-4dd0-94e7-33011a193349"
  },
  "id": "42e4e501b0df4a9e9ecf22b66d70763f"
}
October 6, 2021 12:26 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:26:43.4833778Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "88e8b16c-3d56-40cc-b91f-ac5949979b4d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21121778",
    "VehicleOrderId": "49abf903-3344-4a2c-a531-d5812a20fb18"
  },
  "id": "68f2fc7f71814d6181554fa5cc623ba3"
}
October 6, 2021 12:15 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:15:54.7850606Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "bc5462b4-3f2f-498f-8761-c36bd56ac554"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21353063",
    "VehicleOrderId": "77e319a1-41b5-43e6-b7cd-63e34ec43bb4"
  },
  "id": "fc593e2c404a4ef1aebb7e2413cc3508"
}
October 6, 2021 12:12 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:12:23.5590096Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "20bcc568-ebbb-42aa-a038-c2dc040dd6c9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20420738",
    "VehicleOrderId": "4d5f5c66-1358-4591-8875-f322a16118a0"
  },
  "id": "28583f8d0b364e769d7e70eeac8cede6"
}
October 6, 2021 12:03 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:03:14.6875582Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1f972235-75fa-4af4-b9d5-d9538d27be67"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21160426",
    "VehicleOrderId": "d1b7e1b1-bb2c-49d8-9963-13d0bf084ab8"
  },
  "id": "6a9670f57225417faf73c93113bf8634"
}
October 6, 2021 12:01 AM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T04:01:41.4388039Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "092643e7-cdb6-4822-b1ce-40d65ba26080"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20192535",
    "VehicleOrderId": "989c36b7-91f5-437e-8399-e342a2e28dfb"
  },
  "id": "f1ee7d4ccfff414f9c895d2e218587ec"
}
October 5, 2021 11:46 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T03:46:29.503199Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1cf88bc0-a0dc-404c-ae00-6c884de153c9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20938777",
    "VehicleOrderId": "ff0a44d2-5901-4418-b2da-373a66260416"
  },
  "id": "e4bcbd6ab1694298b46e2484e7b447af"
}
October 5, 2021 11:39 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T03:39:12.9187305Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "52d98f18-6eff-4115-872a-ef0ad91778b4"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20713222",
    "VehicleOrderId": "3d59b425-8123-4311-a5c6-16278d0acc34"
  },
  "id": "eccb2c3a514347b9b8a1011706963a60"
}
October 5, 2021 11:08 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T03:08:21.5325864Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "901e9923-3791-458b-bc11-65986b5fab7d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21049360",
    "VehicleOrderId": "ee47c8e6-badf-4b26-97f7-8883ab410026"
  },
  "id": "56be8d0c5ac54e6a830152de0b0d6c6e"
}
October 5, 2021 10:54 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T02:54:57.3447212Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "0d9d50ac-b415-4ee1-aec5-858275dfd629"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0016R000036N30SQAS"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "264427"
      }
    ],
    "StockNumber": "20812635",
    "VehicleOrderId": "e0301bfe-652a-4fc4-9885-1b893fa595a0"
  },
  "id": "88ddd4e606ef4d019ea941e4806d84f5"
}
October 5, 2021 10:43 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T02:43:02.2426587Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "4900ae35-a78f-4225-934e-d13b4e133ae8"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "129228"
      }
    ],
    "StockNumber": "20876489",
    "VehicleOrderId": "8882142b-94ef-452f-8c54-863408b2bb37"
  },
  "id": "7fc8ccb74a5f44f9a55b1e256bc4e7e2"
}
October 5, 2021 10:33 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T02:33:36.3900986Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "e3485ea5-8640-450e-931e-0fc8fbb9b1b8"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20781050",
    "VehicleOrderId": "cbb3df84-443c-4351-b34b-8524d6c5fd4d"
  },
  "id": "e587579a278a4fe1bb5cb0553e16c817"
}
October 5, 2021 10:30 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T02:30:30.5331806Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "e3485ea5-8640-450e-931e-0fc8fbb9b1b8"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20781050",
    "VehicleOrderId": "cbb3df84-443c-4351-b34b-8524d6c5fd4d"
  },
  "id": "adf38419292d4b209a81c884735869e3"
}
October 5, 2021 10:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T02:22:38.4176913Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "32220cb7-870a-4fd2-8287-503e5d0bae0e"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "229390"
      }
    ],
    "StockNumber": "20993668",
    "VehicleOrderId": "e503cb1a-d0d3-4712-9ea3-250bf0645eca"
  },
  "id": "5c6bec36fbdc42128b5d9ede2f8a255d"
}
October 5, 2021 9:58 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:58:41.8741825Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "790fe590-be58-4779-ad2e-2743d590b641"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21025810",
    "VehicleOrderId": "0e7dcd42-bbff-4d55-8434-469345ca656c"
  },
  "id": "255dc59ca0654a23a4fb32cb27e1e084"
}
October 5, 2021 9:54 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:54:04.69691Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "c72faec6-39ae-4a84-a1dc-719bdb6dcf7f"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21253510",
    "VehicleOrderId": "f813ae14-d6c4-4352-bfa7-d5cce7a9a185"
  },
  "id": "bc5bba3923964dd39efdf7bdeecd9c3c"
}
October 5, 2021 9:53 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:53:25.6945113Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "c9a9e62d-675d-443f-b182-22b5c227427a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21309331",
    "VehicleOrderId": "119cd1dd-fc82-4605-b21f-857ad6ed196f"
  },
  "id": "83a33ed5aca8451c8f3fcab21d3d9946"
}
October 5, 2021 9:52 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:52:25.5938515Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "c9a9e62d-675d-443f-b182-22b5c227427a"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21309331",
    "VehicleOrderId": "119cd1dd-fc82-4605-b21f-857ad6ed196f"
  },
  "id": "0b8f36263bdd46898682ddc47ef9d294"
}
October 5, 2021 9:27 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:27:44.9603864Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "cd13d7be-c707-4204-91a9-01d0bbf92bc5"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "252163"
      }
    ],
    "StockNumber": "20423470",
    "VehicleOrderId": "653d1954-ccb6-4040-b8ec-eaecf55f0957"
  },
  "id": "4c745eda1469456fabd5ff7ae4775363"
}
October 5, 2021 9:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:19:47.3639849Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "f001ae17-941b-4133-8723-a24301442434"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21273200",
    "VehicleOrderId": "e4f1caae-dd0e-4a2d-b466-fcf6425e7b63"
  },
  "id": "6d59a3067359464e93269523bf29cf8a"
}
October 5, 2021 9:14 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:14:18.0000052Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "54e2fa97-31bf-49d7-92d6-40bf85a55dc7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21089442",
    "VehicleOrderId": "137840e8-cd60-460c-b2ca-95238d941420"
  },
  "id": "050979cc3a544dec868e907334463156"
}
October 5, 2021 9:08 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:08:29.1115442Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7ee744ec-69f2-4986-909c-5d96e58292a6"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21332962",
    "VehicleOrderId": "1aca7875-f4a8-4f8f-ad9f-d3f0617b2c22"
  },
  "id": "1fad3407a4744be7a7e4d6743ccc9f39"
}
October 5, 2021 9:06 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T01:06:22.2674298Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "97dd7846-527b-448d-96f2-de8108ffc0aa"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20971169",
    "VehicleOrderId": "34b019c8-9fe9-43d0-9d4b-34e93e737101"
  },
  "id": "a071edd5b2a645ca871df6b6204eb701"
}
October 5, 2021 8:42 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T00:42:24.5512541Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "abafa20a-2778-46b1-b1be-963520555077"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "239633"
      }
    ],
    "StockNumber": "21207247",
    "VehicleOrderId": "17d65145-e05a-460c-a778-dd57d1365edb"
  },
  "id": "49ed5aca62c547dd91823e30784fdeed"
}
October 5, 2021 8:37 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T00:37:43.3311939Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "908b6d8b-9aa7-4d66-a94f-b4990b03b5e9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21157859",
    "VehicleOrderId": "83d97e58-1c61-43fd-812b-7955f040dc63"
  },
  "id": "589d85caa6604779ab8818cf962bde18"
}
October 5, 2021 8:25 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T00:25:00.1847203Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7fcea4e4-e92c-481f-acd9-8175bcfc2b75"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20608201",
    "VehicleOrderId": "0105908b-0e5a-4768-a912-eade00f7453d"
  },
  "id": "f5bc47d3d45c49308daba4b23325fdb1"
}
October 5, 2021 8:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T00:19:50.0472047Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "41414486-979a-4038-bcbd-a4ef359b4ba7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20593052",
    "VehicleOrderId": "14723fe0-05c8-4b17-a2ac-e6713717f861"
  },
  "id": "e9f2734714024f18bd4c9c8b4673a9ea"
}
October 5, 2021 8:10 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T00:10:47.8554517Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "8340a210-3c80-4678-8328-ff263a4303a2"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "227652"
      }
    ],
    "StockNumber": "21076379",
    "VehicleOrderId": "176cb465-230c-431a-bfb7-7c46416ab627"
  },
  "id": "1d6e39d0d519457ab241ecbec054adb2"
}
October 5, 2021 8:04 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-06T00:04:19.9158815Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a99ccf5c-7a90-4639-8e79-2714ce45e53d"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21063168",
    "VehicleOrderId": "22a6bd06-4c42-4248-8b55-36864234e54f"
  },
  "id": "2e7c040a2a2f4827ae008f14643a4474"
}
October 5, 2021 7:44 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:44:50.3744332Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d7ccbf6f-ee76-4ea2-be62-7ddccfeb9ced"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "263387"
      }
    ],
    "StockNumber": "21162525",
    "VehicleOrderId": "eb5637d8-bf7d-4075-807e-1fa3e6096c0f"
  },
  "id": "434d6db3c6c74aaa8489b6ec92953a1b"
}
October 5, 2021 7:43 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:43:30.353865Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "261bf674-c668-4644-b2a9-a874008dd928"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "227123"
      }
    ],
    "StockNumber": "20927694",
    "VehicleOrderId": "a04c9598-a952-442b-8cb4-c83adbb3e3c2"
  },
  "id": "b4de5bd9e11d4cc69a42303adebb2cb5"
}
October 5, 2021 7:40 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:40:36.2472247Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a1af9965-791f-49fd-bbc7-a4c51cb39c37"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20777177",
    "VehicleOrderId": "8979d9da-bd45-4102-809a-10800d7180a0"
  },
  "id": "92587b01bffb41fdaa07cc699f896366"
}
October 5, 2021 7:32 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:32:27.910599Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "908b6d8b-9aa7-4d66-a94f-b4990b03b5e9"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21157859",
    "VehicleOrderId": "83d97e58-1c61-43fd-812b-7955f040dc63"
  },
  "id": "6675a36df6bc49748065258044ad2daa"
}
October 5, 2021 7:23 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:23:54.8170943Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a178aa4c-4e91-42d8-9d3c-1f9d969b2bfc"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21397451",
    "VehicleOrderId": "715bf8b3-e2f6-423f-8e6f-0815d17a1234"
  },
  "id": "1a4b7c01878e4d85b7b380c60a086806"
}
October 5, 2021 7:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:18:06.233356Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "1576cc87-bf34-4b45-a727-033a8d3a0b2c"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": "0011C00002pNVScQAO"
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "256304"
      }
    ],
    "StockNumber": "20993013",
    "VehicleOrderId": "fc77965c-d5ab-4235-8c94-ce00985fb25e"
  },
  "id": "03cc64cb43e34f3e985e02756314ef5a"
}
October 5, 2021 7:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:17:20.4155069Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "a1af9965-791f-49fd-bbc7-a4c51cb39c37"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20777177",
    "VehicleOrderId": "8979d9da-bd45-4102-809a-10800d7180a0"
  },
  "id": "4b7f8c1ede784e669bf32de5b1cec881"
}
October 5, 2021 7:04 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:04:16.2687157Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d07acb85-e471-4798-a9a7-626a54df6bf7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21004543",
    "VehicleOrderId": "dd28f23a-6fb6-4817-bf52-c5d4172a9495"
  },
  "id": "ef68d66f842d4894ad7c99bfdd0f4be3"
}
October 5, 2021 7:01 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T23:01:38.937585Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "3994d838-0378-4a32-814a-5f33a845e304"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21332658",
    "VehicleOrderId": "9381b4c9-4dc8-4335-8eab-e10033ee8e7b"
  },
  "id": "469d3f1685694d0cb5c575f0347b1eae"
}
October 5, 2021 6:54 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:54:17.3544549Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d404ea02-d0d2-4385-8441-371fca23f8ba"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21165310",
    "VehicleOrderId": "6a6ee513-ebb9-47b6-8f75-a10d74b38842"
  },
  "id": "b621f76d14674e95bd26d518161a96ea"
}
October 5, 2021 6:51 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:51:38.0743295Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "cff27a6f-000c-43fe-b4af-b0e12c808885"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20677093",
    "VehicleOrderId": "16d233e9-4532-4419-a69e-e5f401aaebae"
  },
  "id": "39a78864f61d4724b205a9cfec7a772c"
}
October 5, 2021 6:41 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:41:37.0156662Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7ab14a86-9ccb-4c0d-8398-3990c3ebc902"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21333165",
    "VehicleOrderId": "2c5a843c-35e0-469e-be48-d7b36f1fd7ac"
  },
  "id": "42d7e523f73340b0905f7f5f984f0fbf"
}
October 5, 2021 6:34 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:34:39.4470404Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "ccc3fad4-497c-46ab-b695-2a564a4b8988"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21134413",
    "VehicleOrderId": "24652e95-9027-4427-abd8-5b494725920a"
  },
  "id": "0b640945da8249169f5d40dbbcdd5611"
}
October 5, 2021 6:33 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:33:17.8236666Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "8bdb0108-60f5-49e3-8f81-436ba0e61053"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20664018",
    "VehicleOrderId": "556e1195-ff5e-49eb-9c30-0c9362cab079"
  },
  "id": "d6364b387dfd42029feddd2eb9bf2e7b"
}
October 5, 2021 6:11 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:11:57.8486066Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "56ca95eb-b15e-4d0e-813c-9ba2063a932b"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21188857",
    "VehicleOrderId": "eb2ff068-ca6f-4661-a9fc-e1151ee53891"
  },
  "id": "94dc0eeb9f5946688fd46c769054fe09"
}
October 5, 2021 6:09 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:09:19.9545274Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7ab14a86-9ccb-4c0d-8398-3990c3ebc902"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21333165",
    "VehicleOrderId": "2c5a843c-35e0-469e-be48-d7b36f1fd7ac"
  },
  "id": "25c1069941c9415ca75a04e1ed42d623"
}
October 5, 2021 6:08 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:08:10.2785267Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "8f7b0197-5650-41df-a9a6-ddbe59af8128"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21146334",
    "VehicleOrderId": "9b748c15-4210-411b-b362-4d63654090df"
  },
  "id": "faa3c908cce442a3b41bea08b6eb0839"
}
October 5, 2021 6:05 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T22:05:30.5140193Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "aa0ed042-bf06-41cf-b113-ac7aebeab0ee"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21201289",
    "VehicleOrderId": "57aa3e1b-506e-43f1-a906-edccd677b781"
  },
  "id": "241e4bf4b6fd4dbd881b6324dc87f647"
}
October 5, 2021 5:49 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T21:49:43.3300757Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7ab14a86-9ccb-4c0d-8398-3990c3ebc902"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21333165",
    "VehicleOrderId": "2c5a843c-35e0-469e-be48-d7b36f1fd7ac"
  },
  "id": "0807d1d2b627455da6cfb467abfc0a59"
}
October 5, 2021 5:45 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T21:45:21.4684657Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d07acb85-e471-4798-a9a7-626a54df6bf7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21307009",
    "VehicleOrderId": "f1281860-5e5c-4c78-81ce-db51a2c357d0"
  },
  "id": "476db3d444834c68af2b11126494a929"
}
October 5, 2021 5:36 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T21:36:30.3798721Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "d07acb85-e471-4798-a9a7-626a54df6bf7"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21307009",
    "VehicleOrderId": "f1281860-5e5c-4c78-81ce-db51a2c357d0"
  },
  "id": "08abfb66f7354a65b23418ae954b55eb"
}
October 5, 2021 5:29 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T21:29:46.6124365Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "6758a897-92c6-428e-95d5-339862b168c0"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21279737",
    "VehicleOrderId": "016fceec-04a9-42df-b813-6d78c61cde47"
  },
  "id": "b9730bc9995a42378082a201d4074809"
}
October 5, 2021 5:14 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T21:14:32.1269277Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "7ab14a86-9ccb-4c0d-8398-3990c3ebc902"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21333165",
    "VehicleOrderId": "2c5a843c-35e0-469e-be48-d7b36f1fd7ac"
  },
  "id": "95fd571243024d5fb1719f9b3ec7ea04"
}
October 5, 2021 5:04 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T21:04:34.3577817Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "226d9e8d-c44a-4b47-8d7d-1ed62da04c77"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "20850592",
    "VehicleOrderId": "1f8ec593-925b-4423-bed2-f796d0a5e9e2"
  },
  "id": "8bc5085fd13e40ea895493e6c1976cb7"
}
October 5, 2021 5:02 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T21:02:14.9703157Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "dc645119-3d71-4019-a342-a36a00dbf453"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": null
      }
    ],
    "StockNumber": "21349842",
    "VehicleOrderId": "3ef720d2-cde2-428a-9664-dcb0993e8c02"
  },
  "id": "e1d3476e2b87436ba63288cce1e240fb"
}
October 5, 2021 4:54 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "source": "https://vehicleorder-service.buys.carmax.com",
  "subject": "com.carmax.sales.vehicle-order.maxcare.selected.v1",
  "time": "2021-10-05T20:54:19.3866551Z",
  "dataContentType": "application/json",
  "data": {
    "Identities": [
      {
        "Rel": "NotSet",
        "Type": "CiamId",
        "Value": "bda848d0-0a3c-48f8-b00d-3109d41272a2"
      },
      {
        "Rel": "NotSet",
        "Type": "CrmId",
        "Value": null
      },
      {
        "Rel": "FirstAssigned",
        "Type": "AssociateId",
        "Value": "200592"
      }
    ],
    "StockNumber": "21043134",
    "VehicleOrderId": "383a4dad-5834-457b-a101-fb897d8761c1"
  },
  "id": "e6f65efc34d14fefaeac077850079fcc"
}
'''

# COMMAND ----------

maxcare_sample_json = json.loads('[' + re.sub('October \d. \d{4} \d{1,2}:\d{2} [AP]M', ', ', maxcare_sample_string) + ']')

# COMMAND ----------

def parse_maxcare_identity_array(id_arr):
  id_dict = {entry['Type']: entry['Value'] for entry in id_arr if not entry['Value'] is None}
  return id_dict

def flatten_maxcare_obj(dct):
  new_dct = dct
  new_dct['data']['Identities'] = parse_maxcare_identity_array(dct['data']['Identities'])
  return new_dct

# COMMAND ----------

maxcare_sample_json_flattened = []

for obj in maxcare_sample_json:
  maxcare_sample_json_flattened.append(flatten_maxcare_obj(obj))

# COMMAND ----------

#id type prevalence
id_types = []
for obj in maxcare_sample_json_flattened:
  id_types.extend(obj['data']['Identities'].keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

#data key prevalence
id_types = []
for obj in maxcare_sample_json_flattened:
  id_types.extend(obj['data'].keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

#obj key prevalence
id_types = []
for obj in maxcare_sample_json_flattened:
  id_types.extend(obj.keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Event: Customer Progression Updated
# MAGIC 
# MAGIC **Of the full list of events currently published, this is the one I'm most excited about**
# MAGIC 
# MAGIC More details forthcoming with 10/14 meeting, but seems like a valuable event even without enrichment, due to the inclusion of updateReason and updateActivityType fields
# MAGIC 
# MAGIC [https://messaging.sites.carmax.com/event-types/a6d9a10c-053f-4985-ba8e-3588e0b0bfcb](https://messaging.sites.carmax.com/event-types/a6d9a10c-053f-4985-ba8e-3588e0b0bfcb)
# MAGIC ```
# MAGIC {
# MAGIC   "specVersion": "1.0",
# MAGIC   "type": "com.carmax.customer.progression.updated.v1",
# MAGIC   "source": "https://customer-progression-service.carmax.com",
# MAGIC   "subject": "com.carmax.customer.progression.updated.v1",
# MAGIC   "time": "2021-10-07T18:23:28.2319006Z",
# MAGIC   "dataContentType": "application/json",
# MAGIC   "data": {
# MAGIC     "identities": [
# MAGIC       {
# MAGIC         "value": "0016R000036ObC3QAK",
# MAGIC         "type": "crmId"
# MAGIC       },
# MAGIC       {
# MAGIC         "value": "7814d44f-4c75-4abd-83f6-8f3b1a7aec47",
# MAGIC         "type": "ciamId"
# MAGIC       }
# MAGIC     ],
# MAGIC     "updateReason": "ProgressionActivity",
# MAGIC     "updateActivityType": "PreApprovalSubmitted"
# MAGIC   },
# MAGIC   "id": "8aa9951448a54f21ac63dcca949bc558"
# MAGIC }
# MAGIC ```

# COMMAND ----------

progression_update_sample_string = '''
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:23:28.2319006Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ObC3QAK",
        "type": "crmId"
      },
      {
        "value": "7814d44f-4c75-4abd-83f6-8f3b1a7aec47",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalSubmitted"
  },
  "id": "8aa9951448a54f21ac63dcca949bc558"
}
October 7, 2021 2:23 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:23:12.6898069Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d1579262-5483-4473-9e60-fb9022f32b10",
        "type": "ciamId"
      },
      {
        "value": "0016R000036Ogy2QAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "cf2e1a12ab524004862cccc7d94e27c8"
}
October 7, 2021 2:23 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:23:09.5524179Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "57c6adef-fa44-4a75-98d5-8c4332e27fce",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OdPPQA0",
        "type": "crmId"
      },
      {
        "value": "0016R000036OepDQAS",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "04182d934b49473dadbb63d1e41d9474"
}
October 7, 2021 2:23 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:23:08.9397024Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "e684f30d-35ff-4b7f-bb04-2d28d329de7d",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OEdlQAG",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "a8b9189f5aa840618c7169167b0f3c75"
}
October 7, 2021 2:23 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:23:08.7502677Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OdPPQA0",
        "type": "crmId"
      },
      {
        "value": "0016R000036OepDQAS",
        "type": "crmId"
      },
      {
        "value": "57c6adef-fa44-4a75-98d5-8c4332e27fce",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "TransferCheckoutCreated"
  },
  "id": "c74c028613be4d039a22827735de0931"
}
October 7, 2021 2:23 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:23:08.5092858Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "24162dc7-8efc-4e4f-b215-9711141481da",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "56254196b82a49ce844cb6a955130671"
}
October 7, 2021 2:23 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:23:02.6315921Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ObWwQAK",
        "type": "crmId"
      },
      {
        "value": "f9467142-2842-478f-9422-a0ad8f00bc35",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "04bd18f69917448d9c17f8b214482b56"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:59.436187Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "01cc78b5-5076-4897-a3df-760ed8180d71",
        "type": "ciamId"
      },
      {
        "value": "0016R000036Ml1pQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "30ba5f3778b04a75be2169a0cd9f7c3e"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:55.4016234Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ObWwQAK",
        "type": "crmId"
      },
      {
        "value": "f9467142-2842-478f-9422-a0ad8f00bc35",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "b109c400eb274ede9c0497f577c6bb2d"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:53.9922866Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OcVGQA0",
        "type": "crmId"
      },
      {
        "value": "feb321d5-8505-4aeb-876e-a6f561d7679e",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "0e6900cbd4b642cab86b70877ba79a38"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:53.6884776Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d1579262-5483-4473-9e60-fb9022f32b10",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "42cbc0bb141c4261879e7cbdcb03ad81"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:53.0142382Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002VHN4SQAX",
        "type": "crmId"
      },
      {
        "value": "c7937893-64c1-4a45-bb4f-1cef698742a2",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "4b8a6a74712d4b7daf6963dc7cd12952"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:52.6074742Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C000021S3YhQAK",
        "type": "crmId"
      },
      {
        "value": "e8ce015e-21d3-4a38-8444-a47b000525d5",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "c55bea0c97b84af18631f7ec54a9e344"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:42.6172141Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "acba68be-652d-48b9-b624-a52ef3b57345",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgwuQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "56f02203bed34aefaf767340c79af322"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:41.7951779Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ObWwQAK",
        "type": "crmId"
      },
      {
        "value": "f9467142-2842-478f-9422-a0ad8f00bc35",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "3b071d603b274267895a28554716c3eb"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:40.1492929Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d1579262-5483-4473-9e60-fb9022f32b10",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "f079e2ec1c5443d8936e27c7e2ec7e58"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:32.8269512Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C000030rYAmQAM",
        "type": "crmId"
      },
      {
        "value": "abb8e820-1527-4eee-8de0-1a552de4aeac",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "605fd066d4e143c7b80917fa45ddc8bc"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:28.6965407Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002q7Wi2QAE",
        "type": "crmId"
      },
      {
        "value": "8e151247-a361-4211-bf43-69d7813d72d2",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "099ee0a04aa949498083991ed2ab51d9"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:21.1310839Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "4edd1b57-8628-48fb-b9c5-8e70fa7da436",
        "type": "ciamId"
      },
      {
        "value": "0011C00002LglTRQAZ",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "82bf9593324f4fc5a8f3f3b5425f53e1"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:13.5803257Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0883148d-4d92-46d1-aac6-3d1b9f93019c",
        "type": "ciamId"
      },
      {
        "value": "0011C00002kV8qVQAS",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "fb1942f042094b8587f362694401ccdb"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:10.1389616Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OCeiQAG",
        "type": "crmId"
      },
      {
        "value": "ec874dd7-9a3a-419f-b5c3-e83eee1251fd",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "caa22d09c3644970858b5de6831b95c0"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:07.1417048Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "acba68be-652d-48b9-b624-a52ef3b57345",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "db9d8a7ba5234ba3bd11ff60c9048229"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:06.1518896Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OCeiQAG",
        "type": "crmId"
      },
      {
        "value": "ec874dd7-9a3a-419f-b5c3-e83eee1251fd",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "712a3511c38241a297758ba3baaba804"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:05.0100382Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "c3e270d7-e1b9-4c5e-9ed3-c2244469d44e",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OfYwQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderDeleted"
  },
  "id": "4af55ed8afc3466abd6e663e069da939"
}
October 7, 2021 2:22 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:22:04.611722Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "583d2179-84c5-4308-b75b-dcaf5ad791f3",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgwaQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "b0d64f6115034e6ca85705a6bde452db"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:51.9088622Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "583d2179-84c5-4308-b75b-dcaf5ad791f3",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "fba9c43038414427a00eb283b5f9ea5e"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:50.4737931Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OCeiQAG",
        "type": "crmId"
      },
      {
        "value": "ec874dd7-9a3a-419f-b5c3-e83eee1251fd",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "af643b2abb2b4ad09e1f2e9e30d988cd"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:43.7112729Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d701d5f3-cae4-4c57-823b-48f272ccbf3c",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgvwQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "f8b0c75d4e8a4bcabdb8716b1f11e789"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:41.2547359Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgtSQAS",
        "type": "crmId"
      },
      {
        "value": "668cb946-4931-483b-b2a4-fa107a77c136",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "f00d55f73cc1493a88c265ee87fdddd2"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:41.0884261Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgvIQAS",
        "type": "crmId"
      },
      {
        "value": "7b4d3d44-320b-4a1c-a608-d3fe534cc1dc",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "d32ca0ed5d244bf7b3fdf61a0daaf28e"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:39.4694665Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OdrmQAC",
        "type": "crmId"
      },
      {
        "value": "ba9255d4-6d48-4735-abb6-99bfa1e1acf1",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalReceivingDone"
  },
  "id": "73701ec6922f496cad7d0864ab143876"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:35.5325361Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "583d2179-84c5-4308-b75b-dcaf5ad791f3",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "TransferCheckoutCreated"
  },
  "id": "8904c17fb78845188160188a9cc1dd9c"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:33.0605723Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OguZQAS",
        "type": "crmId"
      },
      {
        "value": "068eeee8-7035-4cfe-a6da-ead3557a7150",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "655e33fc76ef40228b0a7f7e73118132"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:31.0069113Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036Og1zQAC",
        "type": "crmId"
      },
      {
        "value": "875467f8-2915-4e00-be6f-a54b00480164",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "f233b6a56d6e491a88def58a402e16f0"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:24.7872032Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "3838b58e-2bf0-4b90-9e7f-a4790044c56e",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "4e4b4dba5b214fe688a106f23c251581"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:23.7883205Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgjwQAC",
        "type": "crmId"
      },
      {
        "value": "a8e184b5-7f0b-4596-b59a-349affd33c72",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "aa82d953a9aa4557969c2201b6edead5"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:21.0850548Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "668cb946-4931-483b-b2a4-fa107a77c136",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "4bea081622a44189b10c566c3d846270"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:20.9883581Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "48f6f661-6cd5-449e-932b-c8a3bc054eb7",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgsdQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "e94baeec54d8447380e117b3eba30e9b"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:20.5701796Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036NfvBQAS",
        "type": "crmId"
      },
      {
        "value": "cfca64fe-a7e8-4859-95e6-8448719095cf",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "08d23edfa7614da2ba0b2206fcbb9eb1"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:18.6932134Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OguZQAS",
        "type": "crmId"
      },
      {
        "value": "068eeee8-7035-4cfe-a6da-ead3557a7150",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "6b8a754b65cf42acb8a237edec92b682"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:18.0429017Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036NfvBQAS",
        "type": "crmId"
      },
      {
        "value": "cfca64fe-a7e8-4859-95e6-8448719095cf",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "6c270335c1e04dddb5363da25e3d6e27"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:15.6177672Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d701d5f3-cae4-4c57-823b-48f272ccbf3c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "b44f060fda0c4ce6ba800c4b149b3e6c"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:12.7560892Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b028b969-0e03-44f7-99a1-c64a22eb4e25",
        "type": "ciamId"
      },
      {
        "value": "0011C000020T4ByQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "TransferCheckoutCompleted"
  },
  "id": "c14ac53ac81e4047899f51986aff87d0"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:06.8892736Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000035cWVGQA2",
        "type": "crmId"
      },
      {
        "value": "c1db42a9-9fd6-43c4-8442-e859d8eaa84c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "b6653a867dc9462299f10aa67646da0b"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:05.9307224Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "668cb946-4931-483b-b2a4-fa107a77c136",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "be2f01f6bc454cee91a6aeb3b027b054"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:03.4071309Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "4e124ca7-d259-428c-9d51-93a99ba5db4c",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgndQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "1e8de64b27c445d6949b9ec27a670321"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:02.6358065Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OguZQAS",
        "type": "crmId"
      },
      {
        "value": "068eeee8-7035-4cfe-a6da-ead3557a7150",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "2bb900ec7a8c4ff7b4864671554f8676"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:01.5989238Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "7b4d3d44-320b-4a1c-a608-d3fe534cc1dc",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "24b15f0e98d34bee8e4d4c69e9871980"
}
October 7, 2021 2:21 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:21:00.7014197Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002ctqK2QAI",
        "type": "crmId"
      },
      {
        "value": "4a74dbb7-53c3-4d40-b3cd-38138c7e13f8",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "dd57746f5099468a817dd72e7c2cd614"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:59.7867156Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d701d5f3-cae4-4c57-823b-48f272ccbf3c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "796ce6192a59490e814b1911bd56ba1f"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:59.6917237Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "7b4d3d44-320b-4a1c-a608-d3fe534cc1dc",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "8210889e210e4d80bdfc1e4a74a475b2"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:58.5939897Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d701d5f3-cae4-4c57-823b-48f272ccbf3c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ProgressionDecision"
  },
  "id": "7276ab0e39104fbab2ba35270751493c"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:57.0014099Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OObaQAG",
        "type": "crmId"
      },
      {
        "value": "93c3b189-7ca0-496d-a889-47adf8f0a49a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalReceivingDone"
  },
  "id": "e9536697ebb143e6a90360c5dc4e9c7a"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:56.6927445Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00001uR3ZKQA0",
        "type": "crmId"
      },
      {
        "value": "dc7c669b-2f10-466b-b8af-508ec9b68080",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "988aff401be040e2a2508fa05645221b"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:56.5096883Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgpUQAS",
        "type": "crmId"
      },
      {
        "value": "2e808c9b-6cf1-49d3-b234-01ff116ebb83",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "d1dc42bd0b01453ca442b747a095072a"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:51.9744861Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "e2998c10-89d2-4be6-be03-e3808a011954",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "e03972134b89467eb50e94e04b351d50"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:51.5935896Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036LtY6QAK",
        "type": "crmId"
      },
      {
        "value": "285931e5-dba5-48da-a308-356e20f8748a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "a8fe6d09a93f45bf8e799ed842dcfb01"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:42.989732Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "7b4d3d44-320b-4a1c-a608-d3fe534cc1dc",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "17f38bdb10a949e6b00f117add8f5f14"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:37.6654087Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "9c5ef149-51db-4d3c-9763-84f0aad0639b",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgrLQAS",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "d9b5aca88710487798616d6c30999406"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:37.3477247Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00001sprt7QAA",
        "type": "crmId"
      },
      {
        "value": "133ea037-3207-4c96-b009-f9b732668aec",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "1bbde081d4de418b91012a724e032526"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:35.603184Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036LUJLQA4",
        "type": "crmId"
      },
      {
        "value": "a86ad34f-aaed-40c8-adbd-f6429eac3b66",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "efb65810fb51440e8c5bd307ae8f2225"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:34.6029763Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b028b969-0e03-44f7-99a1-c64a22eb4e25",
        "type": "ciamId"
      },
      {
        "value": "0011C000020T4ByQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "e039968fcfda4989bd7f6ca093433d84"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:34.30762Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "068eeee8-7035-4cfe-a6da-ead3557a7150",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "1270c7b4ce824c1ba329f860922e4070"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:31.1461575Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b028b969-0e03-44f7-99a1-c64a22eb4e25",
        "type": "ciamId"
      },
      {
        "value": "0011C000020T4ByQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "050f72062e80498ba41621b9863c00ef"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:30.210443Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000361FbbQAE",
        "type": "crmId"
      },
      {
        "value": "c40fab10-4c8f-4958-af3c-5718519c5e61",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "1705c1e7caea46e3ba72ee0c47ff39e8"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:27.324385Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000360loyQAA",
        "type": "crmId"
      },
      {
        "value": "c7f4716b-a66f-4ee7-93ad-23972224b827",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "b84f43a3b6c9439eaf3e52b2c50de57b"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:26.6256047Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "8c16cfca-78f0-4af3-b3b1-f34a9b705094",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OfYcQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "0253a114975b4319a45e2676f66c72f5"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:26.5152759Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OCnBQAW",
        "type": "crmId"
      },
      {
        "value": "f714d7b7-890c-41a9-ad1b-58bc7e730971",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "2153b895364c4e84a9db1dd402aac54b"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:25.0114453Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "78ad389f-ad56-4c5e-96ce-9cbb6b0ff21f",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgtgQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "715021cbe14f4a64a3496ce5f7251807"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:20.6337862Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ORgxQAG",
        "type": "crmId"
      },
      {
        "value": "37cb28e9-a397-4315-a889-86e71051375a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "6d4253ae92ed4e5284d76f070e9b20ba"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:20.3346397Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002HUpMiQAL",
        "type": "crmId"
      },
      {
        "value": "e4695d86-2433-4a2e-8745-77b20f7bbb92",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9c0a1ecab37246ad944ec38373ae5747"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:19.7304357Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgtbQAC",
        "type": "crmId"
      },
      {
        "value": "2c0c5297-4d08-41c7-9ad5-4feff2c73b48",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "44f93c2a19ea46f1b49dc1ec90b616b7"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:18.8283471Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "068eeee8-7035-4cfe-a6da-ead3557a7150",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "08d71fa52c134737860af9b569cfb66f"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:14.5121866Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000361FbbQAE",
        "type": "crmId"
      },
      {
        "value": "c40fab10-4c8f-4958-af3c-5718519c5e61",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "1ed64a16c75a4b408495d000b9acfe33"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:11.0233471Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000360loyQAA",
        "type": "crmId"
      },
      {
        "value": "c7f4716b-a66f-4ee7-93ad-23972224b827",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "334903f3620d4ecc98cc9257ff4d5bcf"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:08.990735Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "a7dedb40-6931-4c2b-8ac9-8b7bcc3a7a8d",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OeL3QAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "ad054992c49647ad8e84440749474c7f"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:20:04.2085442Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011500001dVLcYAAW",
        "type": "crmId"
      },
      {
        "value": "34c9f436-e9da-4e53-8a38-ff77835da40d",
        "type": "ciamId"
      },
      {
        "value": "75128603-2c6f-459e-bbad-9f0b0127edfb",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "02fd0bf4c3aa4a14871de7bd8de2b787"
}
October 7, 2021 2:20 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:59.8220851Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OCnBQAW",
        "type": "crmId"
      },
      {
        "value": "f714d7b7-890c-41a9-ad1b-58bc7e730971",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "887b18990a504a589ecc07cd5301665a"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:59.8171261Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b471da3f-2e4f-4c41-a9be-ea9e47f3ac45",
        "type": "ciamId"
      },
      {
        "value": "0016R000036Ogu5QAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "58eb5f64a8464e1ebfe395a62bf6077a"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:59.573065Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "78ad389f-ad56-4c5e-96ce-9cbb6b0ff21f",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgtgQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "db90b807cdbc4fa195950a3f3c016256"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:57.3705975Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OdZYQA0",
        "type": "crmId"
      },
      {
        "value": "ebf01643-8db3-406c-bf78-dea009cca184",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "3590f4ca4b6340d19e12eb24563dc6d2"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:56.971006Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OObaQAG",
        "type": "crmId"
      },
      {
        "value": "93c3b189-7ca0-496d-a889-47adf8f0a49a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalSubmitted"
  },
  "id": "5740d7988aa44288994dadaacca3dac6"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:49.2927629Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b471da3f-2e4f-4c41-a9be-ea9e47f3ac45",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "6a9e493a67f34077ac81d05ae3cd88b3"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:46.8111239Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b471da3f-2e4f-4c41-a9be-ea9e47f3ac45",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "60ab6eaff0a74e439cec0c25b03abc99"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:45.0968861Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OcLVQA0",
        "type": "crmId"
      },
      {
        "value": "b35d777a-a1d8-4b31-9916-2b12080ec62a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "fbe5d6129ce1403095fc9f96fc2ea9e3"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:44.6938682Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "78ad389f-ad56-4c5e-96ce-9cbb6b0ff21f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "bb9ae26559bd440c86b522f75817dddd"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:41.4816776Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036Of4wQAC",
        "type": "crmId"
      },
      {
        "value": "3bd3316b-f26f-48ab-b0b7-032589e58e5c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9c16d738aad24ac888c527c6c5c6abc0"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:39.3888018Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "c0190bb3-774a-4733-a08e-951b6083cfb5",
        "type": "ciamId"
      },
      {
        "value": "0011C0000221RV5QAM",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "a2acb53b8070412299e51242a09850a4"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:35.4955629Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036MXWbQAO",
        "type": "crmId"
      },
      {
        "value": "aca51d49-be2d-4a2f-8343-5f992740e325",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "e3492f845ac741888ccb0243b9a77295"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:34.8846123Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "78ad389f-ad56-4c5e-96ce-9cbb6b0ff21f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "88160384a4024cf48650ecee900fb925"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:32.6977314Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b471da3f-2e4f-4c41-a9be-ea9e47f3ac45",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "94c89e9cfd1f4a5a829c0a2848ed44ef"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:31.6969267Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "8c488a07-885d-4958-b711-a6979b9cde8a",
        "type": "ciamId"
      },
      {
        "value": "0016R000036LsMnQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "8b165068cb7448668848a74d17efecd8"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:31.2864693Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036NgHHQA0",
        "type": "crmId"
      },
      {
        "value": "14a53f2c-3cbd-4cc9-b45d-9f6bb209fb4f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "d2d3400c0bc64612b360ea341f2b547e"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:28.6185713Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036NgHHQA0",
        "type": "crmId"
      },
      {
        "value": "14a53f2c-3cbd-4cc9-b45d-9f6bb209fb4f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "f81a0d383d74499a91b2c38259b0eaea"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:27.5718022Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002pNNVDQA4",
        "type": "crmId"
      },
      {
        "value": "f8d0affc-b61d-469a-b5b6-a49d0170b774",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "788e9bf1c84f4956bb81b19b9ed54fa0"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:27.2678359Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ORDlQAO",
        "type": "crmId"
      },
      {
        "value": "4ef9bfd0-d539-4a3f-b526-4c7a01523bdf",
        "type": "ciamId"
      },
      {
        "value": "4d4ec5c9-d52f-4224-86cd-f8dc90719b3f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "5f5b65a522fd44ff87efbdd16e2070ce"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:25.2886552Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "ec764c9e-788e-4902-9bc0-eb1d63b9457e",
        "type": "ciamId"
      },
      {
        "value": "0011C00002bmHWQQA2",
        "type": "crmId"
      },
      {
        "value": "0011C00002bmMjTQAU",
        "type": "crmId"
      },
      {
        "value": "0011C00002VJyArQAL",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "715be33f3637487e8878d93a02b9ea94"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:22.8101328Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "78ad389f-ad56-4c5e-96ce-9cbb6b0ff21f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "73298d4742474733a407c303ed33a0be"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:21.0805247Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ORDlQAO",
        "type": "crmId"
      },
      {
        "value": "4ef9bfd0-d539-4a3f-b526-4c7a01523bdf",
        "type": "ciamId"
      },
      {
        "value": "4d4ec5c9-d52f-4224-86cd-f8dc90719b3f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "d4bbd7b53d0240a2b94982d2aae30aa0"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:17.5334742Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "48f6f661-6cd5-449e-932b-c8a3bc054eb7",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "919697b736e04b2282348c9a9c6d14c2"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:16.1663267Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036NgHHQA0",
        "type": "crmId"
      },
      {
        "value": "14a53f2c-3cbd-4cc9-b45d-9f6bb209fb4f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "1a0f2632ef3747f58838023ec9a95e23"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:14.3734712Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "ec764c9e-788e-4902-9bc0-eb1d63b9457e",
        "type": "ciamId"
      },
      {
        "value": "0011C00002bmHWQQA2",
        "type": "crmId"
      },
      {
        "value": "0011C00002bmMjTQAU",
        "type": "crmId"
      },
      {
        "value": "0011C00002VJyArQAL",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "c52579f1df81475ab84c799e7130f9c6"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:14.0833922Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "48f6f661-6cd5-449e-932b-c8a3bc054eb7",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9bfdc39700b741f494c015f4f97714b0"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:12.6458552Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgsOQAS",
        "type": "crmId"
      },
      {
        "value": "f15de911-1242-4dc5-b037-84b658d4779f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "648b41fb99764be6bc1ace3c940da5ac"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:10.8774452Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "48f6f661-6cd5-449e-932b-c8a3bc054eb7",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "57b42ab430e646db8685ba42afb3f5e1"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:08.4943784Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ORDlQAO",
        "type": "crmId"
      },
      {
        "value": "4ef9bfd0-d539-4a3f-b526-4c7a01523bdf",
        "type": "ciamId"
      },
      {
        "value": "4d4ec5c9-d52f-4224-86cd-f8dc90719b3f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "5b65e2e2149145cbaf6ef448d7713570"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:01.143098Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgrfQAC",
        "type": "crmId"
      },
      {
        "value": "e270839e-a79d-468f-8dd3-13678ac55215",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "c71ae3cd20f34714bd62f55468701e3a"
}
October 7, 2021 2:19 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:19:00.9251448Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OL0vQAG",
        "type": "crmId"
      },
      {
        "value": "645ee43f-64ab-4cbf-9b0e-ca0bae5ff502",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "372dbc2eb7ee48af847918cc7869ddcf"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:59.0132958Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002r8o1sQAA",
        "type": "crmId"
      },
      {
        "value": "9f763233-a5cd-469a-b2b2-1d3b51633a58",
        "type": "ciamId"
      },
      {
        "value": "0011C00002r8B0sQAE",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "da71b5ceaaab4e6e80d5ce31cbd4b562"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:58.3486703Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002r8o1sQAA",
        "type": "crmId"
      },
      {
        "value": "9f763233-a5cd-469a-b2b2-1d3b51633a58",
        "type": "ciamId"
      },
      {
        "value": "0011C00002r8B0sQAE",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "TransferCheckoutCreated"
  },
  "id": "57c2ed2bdae44ccd82b8d038db9ac9d4"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:54.311442Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "c8fef7f6-1122-4447-82c0-dea4a32dd51c",
        "type": "ciamId"
      },
      {
        "value": "0016R000036O6KqQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ProgressionDecision"
  },
  "id": "d7ab2d799c864873bf8f66db54e36510"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:53.7150258Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036LVdMQAW",
        "type": "crmId"
      },
      {
        "value": "7a85cb23-7670-42d3-a3a4-6b218c761049",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "65f2a5c086a74c06a3293f998f908c34"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:50.7589846Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "551bdf4a-f710-477d-9d24-45bf443a6f46",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OAHDQA4",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "c65d5cc6812b449ea40cfe71bfcae394"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:47.1516212Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "44c28f54-de88-4bdb-b429-a5ed00ee07a7",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgqrQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "4ffd0ba877624b1ca37d47f3cccc6c57"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:46.2549476Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036ObOEQA0",
        "type": "crmId"
      },
      {
        "value": "7bda160d-842e-404c-af72-6c5aee1f20fd",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "cb162a5b46e94c3d96a8629efaa9d7d9"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:39.4563646Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "f15de911-1242-4dc5-b037-84b658d4779f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "9752b306076c4d30bf12b2248f940a3b"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:33.8639027Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "8fb2972c-2647-43ae-8c4d-d1d26a475d7a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "ff455ea0619f4af498db23fd4d301ed2"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:31.963222Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "db9a2d4f-744c-4104-9af4-5971558326ae",
        "type": "ciamId"
      },
      {
        "value": "0016R000034nFEGQA2",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "61f035bdbd3842db9de1a9f2caf91d4a"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:30.9169709Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "e270839e-a79d-468f-8dd3-13678ac55215",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "b7df5162e3934027812cfefeba8a3e66"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:28.1040813Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "e270839e-a79d-468f-8dd3-13678ac55215",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "6317fd88f925491c9fa844e8f42b3fbe"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:27.6168465Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OeaSQAS",
        "type": "crmId"
      },
      {
        "value": "d537f916-1227-43d1-9ff5-e2b1f18a77fb",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "a930ee58796b46359fd56782b946fd64"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:26.2098832Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002r8B0sQAE",
        "type": "crmId"
      },
      {
        "value": "0011C00002r8o1sQAA",
        "type": "crmId"
      },
      {
        "value": "9f763233-a5cd-469a-b2b2-1d3b51633a58",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "dc24f56e638245aba85a07676393cb12"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:22.8103452Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "3108b92d-9c07-48d6-b2a6-14b1f8fa0a0a",
        "type": "ciamId"
      },
      {
        "value": "0016R000035A04eQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "20b0ab35f1cb4349a1f644553c0dbcb3"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:21.7780209Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C000021PuT9QAK",
        "type": "crmId"
      },
      {
        "value": "e4848d2c-412c-43cc-920a-ae3b9efa4440",
        "type": "ciamId"
      },
      {
        "value": "e7f05c94-46dd-4eb8-a441-8ab08e929987",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "726aba0ba9ee4e4897994702d56edd4f"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:18.480048Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036Of4wQAC",
        "type": "crmId"
      },
      {
        "value": "3bd3316b-f26f-48ab-b0b7-032589e58e5c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "d086383830da47d783c2566f51f10025"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:17.6582904Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "44c28f54-de88-4bdb-b429-a5ed00ee07a7",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgqrQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "b28270354ffb485ba450fb57591e72d3"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:15.1570564Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "e270839e-a79d-468f-8dd3-13678ac55215",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "2981d50ec0ed491d9db0ceb755d1c9c9"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:13.7513906Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "e270839e-a79d-468f-8dd3-13678ac55215",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ProgressionDecision"
  },
  "id": "64f55ccc0cd94330a8b0b7c6cc1eb53a"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:13.681906Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C000026qNV7QAM",
        "type": "crmId"
      },
      {
        "value": "0011C00002uyxAbQAI",
        "type": "crmId"
      },
      {
        "value": "3e79192a-9f8e-426a-b291-15e48908a1c3",
        "type": "ciamId"
      },
      {
        "value": "ea085903-54f6-4fd0-96e2-8bf57a2aec2d",
        "type": "ciamId"
      },
      {
        "value": "13bcaf9c-d184-4966-babf-b17a98ac8765",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "0c954ffc3d6247239b692fa73cde2263"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:12.0198481Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "9c5ef149-51db-4d3c-9763-84f0aad0639b",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "f7457911b8be41b7aa627111029a35ed"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:11.6320786Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "3fbc3c44-e0d3-44bd-825f-a19a0098abb8",
        "type": "ciamId"
      },
      {
        "value": "0011C00002MZ9vcQAD",
        "type": "crmId"
      },
      {
        "value": "0011C00001tUrkwQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "28d953797cc740b28aacb7187ec79895"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:07.624487Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "b5c93bb5-b13b-4128-8b1e-6a1f7953fa23",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OaNkQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "e8ec5bd7b8ea4502a150ff7292314f1e"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:04.6833533Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036Of4wQAC",
        "type": "crmId"
      },
      {
        "value": "3bd3316b-f26f-48ab-b0b7-032589e58e5c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "53916ea8fb2e4557a719c84561d64746"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:02.424456Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OObaQAG",
        "type": "crmId"
      },
      {
        "value": "93c3b189-7ca0-496d-a889-47adf8f0a49a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "a127b77d3d284d1a8d8ef9ac5b9256a1"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:01.097655Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "79a27ffa-dda9-406e-9fe1-5118203308a8",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OfreQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9f05d32705ab4ee4a4aec7228f13f106"
}
October 7, 2021 2:18 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:18:00.3870197Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "44c28f54-de88-4bdb-b429-a5ed00ee07a7",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OgqrQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "0a4df053ec5747dcb0c58670b4bb26f5"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:55.1653144Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00001uvEiKQAU",
        "type": "crmId"
      },
      {
        "value": "0011C00002kbxbnQAA",
        "type": "crmId"
      },
      {
        "value": "124a19d1-3098-4231-b6cc-fd9af691e464",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "0f1b05a27f1049b8a3248dd549ef8cb2"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:55.1233689Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "cb4ec957-858a-4b66-a9bc-187bbfbfa8fa",
        "type": "ciamId"
      },
      {
        "value": "0011C00002zR5ZLQA0",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalReceivingDone"
  },
  "id": "e8cb49c3cc8d47fa83a8265dcac618b1"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:54.9041607Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036MZDWQA4",
        "type": "crmId"
      },
      {
        "value": "804bf992-234b-45fb-9333-eb64e58233ba",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "ab3c16cfd73940a58da402195a2f547e"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:53.5773296Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "9c5ef149-51db-4d3c-9763-84f0aad0639b",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "TransferCheckoutCreated"
  },
  "id": "76aae77a4699440787ab1a2eaf7419d3"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:52.9508911Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OfMqQAK",
        "type": "crmId"
      },
      {
        "value": "4508b6d0-9e11-4396-ae55-85756d8370b6",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderSubmitted"
  },
  "id": "e69d153af49d4897989f3b4384584889"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:51.311123Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OObaQAG",
        "type": "crmId"
      },
      {
        "value": "93c3b189-7ca0-496d-a889-47adf8f0a49a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "31c5bbfc713a4b629507da3d4f595b7e"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:49.4908065Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgjwQAC",
        "type": "crmId"
      },
      {
        "value": "a8e184b5-7f0b-4596-b59a-349affd33c72",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "999126556a994463b671497b22a9f501"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:47.898631Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgjwQAC",
        "type": "crmId"
      },
      {
        "value": "a8e184b5-7f0b-4596-b59a-349affd33c72",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "e8e8ac68bf1a419ebd8afb3186f61851"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:40.6813193Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "44c28f54-de88-4bdb-b429-a5ed00ee07a7",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "3eedbb5fe4ed44b4ae37595d5ff978eb"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:38.2593975Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000035BLKlQAO",
        "type": "crmId"
      },
      {
        "value": "238b580b-2c76-4d34-bf16-90413cf300b6",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "676e5022cac3485ba8ff7ca96ffde5c2"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:36.6129748Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "44c28f54-de88-4bdb-b429-a5ed00ee07a7",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "9e773834a28949938a84de3b8b52a772"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:35.7684019Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002idk6zQAA",
        "type": "crmId"
      },
      {
        "value": "93ed3df3-c06f-4f0b-931b-499905efe14f",
        "type": "ciamId"
      },
      {
        "value": "0011C00002idcfBQAQ",
        "type": "crmId"
      },
      {
        "value": "0011C00002idcfGQAQ",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "63c69fd4a99343699b1dacd0b55c65f1"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:35.477664Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000363YE3QAM",
        "type": "crmId"
      },
      {
        "value": "439da491-c421-459f-9d3e-af9ac37fbe5d",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "0aa105ae5c3646aca5f1f7e68ccbd631"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:30.074459Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "c50ecbed-0c9e-4786-8afe-bd53ae29fceb",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OfClQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "bb965c5e6248492a8edc09ecbbc5aeb1"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:27.9693164Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgiZQAS",
        "type": "crmId"
      },
      {
        "value": "e6476e0e-a0dd-44c4-8c7b-d2f1e885d414",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "8643764e085c41ceb051130fc56447ba"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:21.9619666Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgpKQAS",
        "type": "crmId"
      },
      {
        "value": "d321dd0c-abcd-4522-9d83-494233a50f8b",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "6441f1760bef4d5cac933df08733b952"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:20.6551161Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "44c28f54-de88-4bdb-b429-a5ed00ee07a7",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "24b0e3038e7944698fc871a2a8a772cf"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:19.9856031Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000363YE3QAM",
        "type": "crmId"
      },
      {
        "value": "439da491-c421-459f-9d3e-af9ac37fbe5d",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "e864790563ae4804a201a99833a02742"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:19.6611668Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "44c28f54-de88-4bdb-b429-a5ed00ee07a7",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "TransferCheckoutCreated"
  },
  "id": "2ea6fbfbea424a1692c954758a162b4c"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:18.3665958Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "4a1c99cb-c8e9-4a1c-9d03-39e646a0909d",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OftuQAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "3d32addf8b9e404782d42679bdc61e48"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:16.9180197Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "dd8e1f8c-938b-4e64-bc5c-03767e519725",
        "type": "ciamId"
      },
      {
        "value": "0016R000035ppHfQAI",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "c9d94fa1eb4e46b687ff5072f305e7a5"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:09.7438725Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "95bd61e8-feaa-4575-8531-387966d27bff",
        "type": "ciamId"
      },
      {
        "value": "0016R000036Oge2QAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "2e189fff5aee43a7a3f7c440786e13a7"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:06.5200363Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C0000336mWcQAI",
        "type": "crmId"
      },
      {
        "value": "341f1fce-f7b5-4048-926f-785117125d8c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "954b586fccad415198c0a5b8edde80fb"
}
October 7, 2021 2:17 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:17:04.0213Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C0000238jhdQAA",
        "type": "crmId"
      },
      {
        "value": "84653bfe-997f-4ac5-a3d0-7f88ed3d43d5",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "f0450ce6ce6f46929130fedb3c6a7855"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:53.3417674Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "c831c4f1-4d18-4e3c-ae8b-e53b0373e2f3",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OUgMQAW",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "8f4a2009fe4b418ebb2f35c647fcc626"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:39.6093292Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "1f8e3ef5-83d3-4144-89ea-a06d017757ae",
        "type": "ciamId"
      },
      {
        "value": "0011C00002257ogQAA",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "ec23d048a125483d835392fd274b23ff"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:37.6339989Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036Oge3QAC",
        "type": "crmId"
      },
      {
        "value": "536e2669-a973-45c1-a1fc-fea1f3c1fa4f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "ddf8d74557924e1596c3bf35cd02c9b7"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:35.7710006Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OTb1QAG",
        "type": "crmId"
      },
      {
        "value": "e061f7e4-75df-4e58-b436-20c833483b9a",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "0a73276e133a474590c6f7a8c8d480a8"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:34.9600831Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "30b8c277-711b-4282-8dee-c3e2b97fac15",
        "type": "ciamId"
      },
      {
        "value": "0011C000031YC21QAG",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "b77d685222774ad29f1f34e1fc572c7f"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:32.3523823Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OY4IQAW",
        "type": "crmId"
      },
      {
        "value": "539bf66a-f70b-45e8-bcea-dc96b226ff01",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9c0fef4edd4949aaad33f60a14892205"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:30.6299886Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002LfRBEQA3",
        "type": "crmId"
      },
      {
        "value": "0e325db7-48b4-4ebc-a941-678ffda38adc",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "fd1496b656ac4863a6b4cbedfef9177a"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:26.4392272Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OQETQA4",
        "type": "crmId"
      },
      {
        "value": "004e6276-af91-4125-85c9-806c1cd6050c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "TransferCheckoutCompleted"
  },
  "id": "5c8a5ab035574d4980549781106ea6a2"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:21.8297776Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "1682d497-eaf8-455c-aefe-89be6ad43b02",
        "type": "ciamId"
      },
      {
        "value": "0016R000036MHMTQA4",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9650f85a65b9400bb29c56b713bec42f"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:21.2247848Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000364UbJQAU",
        "type": "crmId"
      },
      {
        "value": "44cd0bd0-cdd0-4400-871c-6c745bc174d8",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "890cce19b4184461bd7b363d38ee7db4"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:21.0354605Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "a652f20c-a1ef-4a85-a577-2e66ddb0e032",
        "type": "ciamId"
      },
      {
        "value": "0011C00002n0s8MQAQ",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "c0183d4e01f54e32b288b07a72cc5bdf"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:19.5741058Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036LqnwQAC",
        "type": "crmId"
      },
      {
        "value": "c15f46b5-d02a-440f-881e-7d2be48bc83c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "331f9d1451e5438fa8242ec5202a2df6"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:18.9199494Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OfMqQAK",
        "type": "crmId"
      },
      {
        "value": "4508b6d0-9e11-4396-ae55-85756d8370b6",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "CreditApplicationReceivingDone"
  },
  "id": "15230165c7874b9ca07015d47e56ae0c"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:17.7404972Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "a6e97ac0-babf-4989-b845-97571cf7b32d",
        "type": "ciamId"
      },
      {
        "value": "0011C000030rm7SQAQ",
        "type": "crmId"
      },
      {
        "value": "b475fd7a-4aef-4a42-b92a-3c9404c85002",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "32207c53a6b9431eb7e6d44a6698897b"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:15.6071023Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036LUJLQA4",
        "type": "crmId"
      },
      {
        "value": "a86ad34f-aaed-40c8-adbd-f6429eac3b66",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "2cd3a56f9ff64b479c5e1108acd4f630"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:13.4072413Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002kRr0yQAC",
        "type": "crmId"
      },
      {
        "value": "808c7635-4e2e-4059-bf34-4b8bc70b9ef2",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9a57961d1e5d4b7f9a49e7df0448cc30"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:12.9684225Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000035ry6XQAQ",
        "type": "crmId"
      },
      {
        "value": "da7ba6f4-aa54-4507-9531-135f25dcc2cf",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "dda0688938d94b6fb8d46c46a64e5d29"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:06.8043924Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "95735b1f-3019-4e03-97dd-5168e26873a9",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OE4DQAW",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "cad12b53cf894860b675c5f2f30190ce"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:05.6109741Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OeNxQAK",
        "type": "crmId"
      },
      {
        "value": "64b1aaa5-0f7e-40f6-bf34-3edd9dd2f36d",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "InstantOfferCompleted"
  },
  "id": "576ca0778e604a918d5e9ffe3f1ed682"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:04.2101382Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OggsQAC",
        "type": "crmId"
      },
      {
        "value": "6642c301-31d1-4db2-9877-776c5e2e92fe",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "0687e9b3f3d54cd381f180093d4646ae"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:02.1460458Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036MKmKQAW",
        "type": "crmId"
      },
      {
        "value": "1a6b0d5e-ae59-4406-98b4-7b4f78d7cf30",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "44caadfdd7c14b8fba23d485134798ac"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:01.5345445Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000361S62QAE",
        "type": "crmId"
      },
      {
        "value": "2b24c3f9-b129-4a09-8758-9f2500e7ef04",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "022aef57f92e4a018510e7a20b07e84a"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:00.9651616Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002VH4wPQAT",
        "type": "crmId"
      },
      {
        "value": "8bcbdb15-882d-4841-9785-220dfc4239ae",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "cf602fdf4a8648e29f21ad64a468d28b"
}
October 7, 2021 2:16 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:16:00.5589066Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036Of31QAC",
        "type": "crmId"
      },
      {
        "value": "97404c11-384d-41df-ac42-a2626a711a4b",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "253e83d7516b426ba081fe6404847461"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:57.0864057Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgnsQAC",
        "type": "crmId"
      },
      {
        "value": "541dd638-734a-487a-8a6b-703e09baf458",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "25c70ff0f237447f8052ce3ace4c61d8"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:53.2774308Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "43972103-1a1c-4247-8ee9-5e42e0378468",
        "type": "ciamId"
      },
      {
        "value": "0011C00002xxd4FQAQ",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "3573f8a5b86c4910b7021540c733ce73"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:53.1925167Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0011C00002VHAUDQA5",
        "type": "crmId"
      },
      {
        "value": "c17cbfda-7209-40e5-890b-f70e8d5ff816",
        "type": "ciamId"
      },
      {
        "value": "0016R000036NuWVQA0",
        "type": "crmId"
      },
      {
        "value": "0011C0000244Y0yQAE",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "c6af25a2fcfc410f8c746e2defe7ff24"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:52.8702397Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OgjxQAC",
        "type": "crmId"
      },
      {
        "value": "02720007-67bc-4f69-8fc9-43f6ad8fb2ed",
        "type": "ciamId"
      },
      {
        "value": "0016R000036Oe6XQAS",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "3ee41db165ce4034b62f1afef3506445"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:52.2859324Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "3c9f4c5c-d3e4-4bf8-93f0-57d0ea9acf14",
        "type": "ciamId"
      },
      {
        "value": "0011C000021SxwLQAS",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "b1e03418f5e24fc7ba3a79c8650f3607"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:45.1410592Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "7f79987d-d574-4dd9-8878-209e68d1dc06",
        "type": "ciamId"
      },
      {
        "value": "0016R000036Oga5QAC",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalReceivingDone"
  },
  "id": "323ee7b1a698408190a085b23a0e0f32"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:44.4896074Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "ebf0a642-aafb-4ad0-8da4-0e24c0d71f50",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "77780416cc134344978d430ff7aa0157"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:42.0445048Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R0000363Y7LQAU",
        "type": "crmId"
      },
      {
        "value": "b0fda3e2-f0c7-4d41-9964-9b0f5cc92513",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "eec741dc90e04695a7f862507342279c"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:40.7377749Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "8c16cfca-78f0-4af3-b3b1-f34a9b705094",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OfYcQAK",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "629ac0a6691945cf8d1805283247e289"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:39.2315753Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OQETQA4",
        "type": "crmId"
      },
      {
        "value": "004e6276-af91-4125-85c9-806c1cd6050c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "9ef2e89a59e64fcaa74a082224a81470"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:36.4464463Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "d4f8c6d3-e771-4fc9-b70c-7ae365cff3a1",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OglXQAS",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "VehicleOrderCreated"
  },
  "id": "acb5f1a65465428fbc59d8bf4dd977b8"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:34.9362817Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "a485ad4f-9231-438d-a7f9-6c15d1914919",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "PreApprovalUpdated"
  },
  "id": "28d50c91c79f48f48df16cc8558d00b0"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:34.5082442Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "30cad56c-4d65-454b-b9bf-413314d0da80",
        "type": "ciamId"
      },
      {
        "value": "0016R000036NQreQAG",
        "type": "crmId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationCreated"
  },
  "id": "d4eaf78ec02c446f983dbbcd264836c6"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:23.7545199Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000035cyXzQAI",
        "type": "crmId"
      },
      {
        "value": "c883da64-5563-45df-9ba2-7f947584209f",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "de4604c24dd1409e933347e3aacd6603"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:22.1431186Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "f60557c7-35ac-467a-85a6-97812c1784d4",
        "type": "ciamId"
      },
      {
        "value": "0016R000036OeMLQA0",
        "type": "crmId"
      }
    ],
    "updateReason": "ProfileUpdate",
    "updateActivityType": null
  },
  "id": "48cd3f503bc34bd9ac504f8b009d64ca"
}
October 7, 2021 2:15 PM
{
  "specVersion": "1.0",
  "type": "com.carmax.customer.progression.updated.v1",
  "source": "https://customer-progression-service.carmax.com",
  "subject": "com.carmax.customer.progression.updated.v1",
  "time": "2021-10-07T18:15:21.3181721Z",
  "dataContentType": "application/json",
  "data": {
    "identities": [
      {
        "value": "0016R000036OQETQA4",
        "type": "crmId"
      },
      {
        "value": "004e6276-af91-4125-85c9-806c1cd6050c",
        "type": "ciamId"
      }
    ],
    "updateReason": "ProgressionActivity",
    "updateActivityType": "ReservationRequested"
  },
  "id": "28f06652d62943eea0e40ad06a64d0a9"
}
'''

# COMMAND ----------

prog_sample_json = json.loads('[' + re.sub('October \d. \d{4} \d{1,2}:\d{2} [AP]M', ', ', progression_update_sample_string) + ']')

# COMMAND ----------

def parse_prog_identity_array(id_arr):
  id_dict = {entry['type']: entry['value'] for entry in id_arr}
  if 'storeCustomerId' in id_dict.keys():
    store_loc_num = [entry['meta']['value'] for entry in id_arr if entry['type'] == 'storeCustomerId'][0]
    id_dict['storeCustomerIdLocationId'] = store_loc_num
  return id_dict

def flatten_prog_obj(dct):
  new_dct = dct
  new_dct['data']['identities'] = parse_prog_identity_array(dct['data']['identities'])
  return new_dct

# COMMAND ----------

prog_json_flattened = []

for obj in prog_sample_json:
  prog_json_flattened.append(flatten_prog_obj(obj))

# COMMAND ----------

#id type prevalence
id_types = []
for obj in prog_json_flattened:
  id_types.extend(obj['data']['identities'].keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

#id type prevalence
id_types = []
for obj in prog_json_flattened:
  id_types.extend(obj['data'].keys())

plt.figure(figsize=(16, 10))
sns.countplot(id_types)

# COMMAND ----------

#updateReason, updateActivityType prevalence
update_types = []
for obj in prog_json_flattened:
  update_reason_activity = f"UR: {obj['data']['updateReason']}, UAT: {obj['data']['updateActivityType']}"
  update_types.append(update_reason_activity)

plt.figure(figsize=(16, 10))
sns.countplot(y=update_types)

# COMMAND ----------


