# backend/routes.py
from flask import Blueprint, request, jsonify
from backend.database import SessionLocal
from backend.models import Voter, Election, Option, VoteRecord, AuditBlock
from backend.auth import hash_password, verify_password
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json

bp = Blueprint('api', __name__, url_prefix='/api')

def append_audit(db, data_dict):
    prev = db.query(AuditBlock).order_by(AuditBlock.id.desc()).first()
    prev_hash = prev.block_hash if prev else '0'*64
    data = json.dumps(data_dict, sort_keys=True)
    new_hash = AuditBlock.compute_hash(prev_hash, data)
    block = AuditBlock(prev_hash=prev_hash, data=data, block_hash=new_hash)
    db.add(block)
    db.commit()

@bp.route('/register', methods=['POST'])
def register():
    db = SessionLocal()
    body = request.get_json() or {}
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        return jsonify({'msg':'username and password required'}), 400
    voter = Voter(username=username, password_hash=hash_password(password), is_admin=False)
    db.add(voter)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return jsonify({'msg':'username exists'}), 400
    append_audit(db, {'action':'register','username':username})
    return jsonify({'msg':'registered'})

@bp.route('/login', methods=['POST'])
def login():
    db = SessionLocal()
    body = request.get_json() or {}
    username = body.get('username')
    password = body.get('password')
    v = db.query(Voter).filter_by(username=username).first()
    if not v or not verify_password(password, v.password_hash):
        return jsonify({'msg':'bad credentials'}), 401
    token = create_access_token(identity={'id': v.id, 'username': v.username, 'is_admin': v.is_admin})
    return jsonify({'access_token': token})

@bp.route('/elections', methods=['POST'])
@jwt_required()
def create_election():
    me = get_jwt_identity()
    if not me.get('is_admin'):
        return jsonify({'msg':'admin required'}), 403
    db = SessionLocal()
    body = request.get_json() or {}
    title = body.get('title')
    desc = body.get('description')
    options = body.get('options', [])
    if not title or not options:
        return jsonify({'msg':'title and options required'}), 400
    election = Election(title=title, description=desc)
    db.add(election)
    db.commit()  # to get id
    for opt in options:
        db.add(Option(election_id=election.id, text=opt))
    db.commit()
    append_audit(db, {'action':'create_election','election_id':election.id,'title':title})
    return jsonify({'msg':'created','id':election.id})

@bp.route('/elections', methods=['GET'])
def list_elections():
    db = SessionLocal()
    elections = db.query(Election).all()
    out = []
    for e in elections:
        out.append({'id': e.id, 'title': e.title, 'description': e.description,
                    'options': [{'id':o.id,'text':o.text,'votes':o.votes} for o in e.options]})
    return jsonify(out)

@bp.route('/vote', methods=['POST'])
@jwt_required()
def cast_vote():
    me = get_jwt_identity()
    db = SessionLocal()
    body = request.get_json() or {}
    election_id = body.get('election_id')
    option_id = body.get('option_id')
    if not election_id or not option_id:
        return jsonify({'msg':'election_id and option_id required'}), 400
    existing = db.query(VoteRecord).filter_by(voter_id=me['id'], election_id=election_id).first()
    if existing:
        return jsonify({'msg':'already voted'}), 400
    opt = db.query(Option).filter_by(id=option_id, election_id=election_id).first()
    if not opt:
        return jsonify({'msg':'invalid option'}), 400
    opt.votes = opt.votes + 1
    vr = VoteRecord(voter_id=me['id'], election_id=election_id, option_id=option_id)
    db.add(vr)
    db.commit()
    append_audit(db, {'action':'vote','voter_id':me['id'],'election_id':election_id,'option_id':option_id})
    return jsonify({'msg':'voted'})

@bp.route('/results/<int:election_id>', methods=['GET'])
def results(election_id):
    db = SessionLocal()
    e = db.query(Election).filter_by(id=election_id).first()
    if not e:
        return jsonify({'msg':'not found'}), 404
    return jsonify({'id': e.id, 'title': e.title, 'results': [{'option':o.text,'votes':o.votes} for o in e.options]})

@bp.route('/audit', methods=['GET'])
@jwt_required()
def audit():
    me = get_jwt_identity()
    if not me.get('is_admin'):
        return jsonify({'msg':'admin required'}), 403
    db = SessionLocal()
    blocks = db.query(AuditBlock).order_by(AuditBlock.id.asc()).all()
    return jsonify([{'id':b.id,'prev_hash':b.prev_hash,'data':b.data,'hash':b.block_hash,'timestamp':str(b.timestamp)} for b in blocks])
