msg_dictionary = {"refuse_answer": "Хорошо, вы можете вернуться к выбору в любое время😌",
                  "start_message":
                  # "Бот поможет выбрать нужную для вас услугу и записаться на нее, а так же связаться с"
                  #              " администратором\n"
                      "Написать администратору - /direct_on\n"
                      "Отключить общение с администратором - /direct_off\n"
                      "/help - помощь 🤖",
                  "confirmation_answer": "Мы вас записали, скоро с вами свяжутся, чтобы уточнить информацию 🤗",
                  "delete_reply": "Клавиатура убрана❌",
                  "dunno": "Я не знаю что с этим делать 🤯",
                  "to_on_direct": "Чтобы отправлять сообщения админитсратору, вы должны перейти в режим общения\n"
                                  "/direct_on - команда перехода в режим общения с администратором",
                  "send_message_to_users": "Введите текст для начала рассылки, отправьте stop чтобы остановить выполнение команды",
                  "already_direct_on": "Вы уже находитесь в режиме общения с администратором 💭",
                  "already_direct_off": "Режим общения с администратором уже выключен",
                  "unknown_command": "Неизвестная команда",
                  "crm_send_error": "<b>Система не смогла загрузить файл, пожалуйста, попробуйте загрузить его самостоятельно:</b>\n",
                  "help": "<b>Команды бота</b>\n"
                          "/sign_up - записаться на процедуру\n"
                          "/direct_on - включить режим общения с администратором\n"
                          "/direct_off - выключить режим общения с администратором\n"
                          "/remove_keyboard - удалить клавиатуру\n"
                          "/help - вызов текущего сообщения",
                  "help_for_admin": "\n\n<b>Администрирование</b>"
                                    "\n/send_message_to_users - рассылка в боте",
                  "direct_on_message": "Бот был переведен в режим общения с администратором, здесь вы можете задать "
                                       "интересющие вас вопросы 💭",
                  "direct_off_message": "Режим общения был выключен",
                  "error": {"simple_error": "Возникла ошибка, попробуйте еще раз",
                            "confirmation_error": "Что-то пошло не так, попробуйте записаться ещё раз, приносим свои "
                                                  "извинения"}
                  }
data_dictionary = {"pm_basic": "Стандартная процедура",
                   "pm_update": "Процедура обновления",
                   "pm_correction": "Процедура коррекции",
                   "eyebrows": "Брови",
                   "lips": "Губы",
                   "eyelids": "Веки",
                   "ekaterina": "Мастер Екатерина",
                   "alina": "Мастер Алина",
                   "eyebrow_design": "Оформление бровей",
                   "eyebrow_coloring": "Окрашивание бровей",
                   "eyelash_coloring": "Окрашивание ресниц",
                   "lamination_of_eyelashes": "Ламинирование ресниц",
                   "smas_lifting": "SMAS-лифтинг",
                   "cosmetic_procedures": "Косметические процедуры",
                   "carbon_peeling": "Карбоновый пилинг",
                   "biorepil_peeling": "Биорепил пилинг",
                   "cold_plasma": "Холодная плазма",
                   "non-surgical_blepharoplasty": "Безоперационная блефаропластика",
                   "personality_diagnostics": "Мастер диагностики личности",
                   "ego_course": "'Эго' работа с Эго-структурами",
                   "coaching_session": "Коуч сессия",
                   "calculation_of_the_fate_matrix": "Расчёт матрицы судьбы",
                   "astrological_consultation": "Астрологическая консультация",
                   "order_natal_chart": "Заказать натальную карту",
                   "find_out_your_purpose": "Узнать своё предназначение",
                   "support": "Сопровождение",
                   "basic_training_from_scratch": "Базовое обучение с нуля",
                   "professional_development": "Повышение квалификации",
                   "basic_all_zones_education": "Обучение по всем зонам",
                   "eyebrow_basic_education": "Курс 'Бровист'"
                   }
lists = {"sphere": {"name": "sphere",
                    "items": {"beauty_btn": "Красота",
                              "soul_btn": "Психология",
                              "education_btn": "Обучение"},
                    "message": "Выберите сферу для записи"
                    },
         "beauty_spheres": {"name": "beauty_sphere",
                            "items": {"permanent_makeup": "Перманентный макияж",
                                      "other": "Другое"},
                            "message": "Выберите услугу, на которую хотите записаться"
                            },
         "permanent_types": {"name": "permanent_type",
                             "items": {"pm_basic": "Основная",
                                       "pm_update": "Обновление",
                                       "pm_correction": "Коррекция"},
                             "message": "Выберите тип процедуры"
                             },
         "beauty_other": {"name": "beauty_other",
                          "items": {"eyebrow_design": "Оформление бровей",
                                    "eyebrow_coloring": "Окрашивание бровей",
                                    "eyelash_coloring": "Окрашивание ресниц",
                                    "lamination_of_eyelashes": "Ламинирование ресниц",
                                    "smas_lifting": "SMAS-лифтинг",
                                    "cosmetic_procedures": "Косметические процедуры",
                                    "carbon_peeling": "Карбоновый пилинг",
                                    "biorepil_peeling": "Биорепил пилинг",
                                    "cold_plasma": "Холодная плазма",
                                    "long-term_eyebrow_styling": "Долговременная укладка бровей",
                                    "non-surgical_blepharoplasty": "Безоперационная блефаропластика"},
                          "message": "Выберите услугу, на которую хотите записаться"
                          },
         "pm_basic": {"name": "pm_basic",
                      "items": {"ekaterina": "Мастер Екатерина",
                                "alina": "Мастер Алина"},
                      "message": "Выберите мастера, к которому хотите записаться"
                      },
         "pm_update": {"name": "pm_update",
                       "items": {"ekaterina": "Мастер Екатерина",
                                 "alina": "Мастер Алина"},
                       "message": "Выберите мастера, к которому хотите записаться"
                       },
         "pm_correction": {"name": "pm_correction",
                           "items": {"ekaterina": "Мастер Екатерина",
                                     "alina": "Мастер Алина"},
                           "message": "Выберите мастера, к которому хотите записаться"
                           },
         "pm_zone": {"name": "pm_zone",
                     "items": {"eyebrows": "Брови",
                               "lips": "Губы",
                               "eyelids": "Веки"},
                     "message": "Выберите зону для записи"
                     },
         "workers": {"name": "workers",
                     "items": {"ekaterina": "Мастер Екатерина",
                               "alina": "Мастер Алина"},
                     "message": "Выберите мастера, к которому хотите записаться"
                     },
         "soul_section": {"name": "soul_section",
                          "items": {"coaching_session": "Коуч сессия",
                                    "calculation_of_the_fate_matrix": "Расчёт матрицы судьбы",
                                    "astrological_consultation": "Астрологическая консультация",
                                    "order_natal_chart": "Заказать натальную карту",
                                    "find_out_your_purpose": "Узнать своё предназначение",
                                    "support": "Сопровождение"},
                          "message": "Выберите услугу, на которую хотите записаться"
                          },
         "education_section": {"name": "education_section",
                               "items": {"permanent_makeup_education": "Перманентный макияж",
                                         "personality_diagnostics": "Мастер диагностики личности",
                                         "ego_course": "'Эго' работа с Эго-структурами"},
                               "message": "Выберите обучение, на которое хотите записаться"
                               },
         "pm_education": {"name": "pm_education",
                          "items": {"basic_training_from_scratch": "Базовое обучение с нуля",
                                    "professional_development": "Повышение квалификации"},
                          "message": "Выберите обучение по преманентному макияжу, на которое хотите записаться"
                          },
         "pm_basic_education": {"name": "pm_basic_education",
                                "items": {"basic_all_zones_education": "Обучение по всем зонам",
                                          "eyebrow_basic_education": "Курс 'Бровист'"},
                                "message": "Выберите вид базового обучения, на который хотите записаться"
                                },
         "confirmation": {"name": "confirmation",
                          "items": {"confirm": "Да",
                                    "refuse": "Нет"},
                          "message": "Вы уверены, что хотите записаться на выбранную услугу?"
                          },
         "back": {"name": "back",
                  "items": {"back": "Назад"}
                  },

         }

reply_keyboards = {"keyboards": {"direct_on": ["direct_on"],
                                 "direct_off": ["direct_off"]},
                   "items": {"direct_on": "Включить режим общения✔️",
                             "direct_off": "Выключить режим общения❌"}
                   }

additional_btns_dict = {"<<": "<<",
                        "back": "Назад",
                        ">>": ">>"}

not_available_procedures = {"ekaterina": ["lamination_of_eyelashes"],
                            "alina": ["long-term_eyebrow_styling", "smas_lifting"]}
